"""
Conversation Manager
Orchestrates the automatic conversation between oncologist and patient
"""
from typing import List, Dict, Optional, AsyncIterator, Callable
from agents.base_agent import BaseAgent
from config.settings import Settings
from utils.tts_manager import TTSManager
import asyncio


class Message:
    """Represents a single message in the conversation"""

    def __init__(self, speaker: str, role: str, content: str, model_info: str = ""):
        self.speaker = speaker
        self.role = role  # "oncologist" or "patient"
        self.content = content
        self.model_info = model_info

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "speaker": self.speaker,
            "role": self.role,
            "content": self.content,
            "model_info": self.model_info
        }

    def to_llm_format(self) -> Dict[str, str]:
        """Convert to LLM API format"""
        # Map our roles to LLM roles (user/assistant alternating)
        llm_role = "user" if self.role == "patient" else "assistant"
        return {
            "role": llm_role,
            "content": self.content
        }


class ConversationManager:
    """Manages the automatic conversation between oncologist and patient"""

    def __init__(
        self,
        oncologist: BaseAgent,
        patient: BaseAgent,
        case_scenario: str,
        max_turns: int = 20,
        stream_callback: Optional[Callable] = None,
        enable_tts: bool = False,
        tts_engine: str = "gtts",
        tts_container: Optional[any] = None,
        session_state: Optional[any] = None
    ):
        """
        Initialize conversation manager

        Args:
            oncologist: Oncologist agent
            patient: Patient agent
            case_scenario: Formatted case scenario text
            max_turns: Maximum conversation turns
            stream_callback: Optional callback for streaming updates
            session_state: Streamlit session state for pause control
        """
        self.oncologist = oncologist
        self.patient = patient
        self.case_scenario = case_scenario
        self.max_turns = max_turns
        self.stream_callback = stream_callback
        self.session_state = session_state

        self.messages: List[Message] = []
        self.turn_count = 0
        self.is_running = False
        self.should_stop = False
        self.is_paused = False

        # TTS configuration
        self.enable_tts = enable_tts
        self.tts_container = tts_container
        self.tts_manager = TTSManager(engine=tts_engine, enable_tts=enable_tts) if enable_tts else None

        # Lightweight dialogue state
        self.agenda_order = [
            "introduction",
            "recommendation",
            "considerations",
            "closing"
        ]
        self.doctor_agenda = {topic: False for topic in self.agenda_order}
        self.patient_concerns = set()  # keywords gathered from patient turns
        self.last_question_by: Optional[str] = None  # "oncologist" or "patient"
        
        # Topic turn tracking for doctor-led conversation flow
        self.current_topic: Optional[str] = None  # Current agenda item being discussed
        self.topic_turn_count: int = 0  # Number of exchanges on current topic
        self.just_transitioned: bool = False  # Flag to track if we just transitioned topics

    def get_conversation_history_for_llm(self, for_role: str) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for LLM API

        Args:
            for_role: "oncologist" or "patient" - who is speaking next

        Returns:
            List of messages in LLM format
        """
        history = []

        for msg in self.messages:
            # From oncologist's perspective: patient messages are "user", their own are "assistant"
            # From patient's perspective: oncologist messages are "user", their own are "assistant"
            if for_role == "oncologist":
                llm_role = "user" if msg.role == "patient" else "assistant"
            else:  # for_role == "patient"
                llm_role = "user" if msg.role == "oncologist" else "assistant"

            history.append({
                "role": llm_role,
                "content": msg.content
            })

        return history

    def _get_next_topic(self) -> Optional[str]:
        """
        Get the next priority topic from the agenda
        
        Returns:
            Next topic key or None if all topics are complete
        """
        for topic in self.agenda_order:
            if not self.doctor_agenda.get(topic, False):
                return topic
        return None

    def _should_transition_topic(self) -> bool:
        """
        Determine if we should transition to the next topic
        
        Returns:
            True if topic should transition (after 2-3 exchanges)
        """
        # Force transition after 2-3 exchanges on current topic
        if self.topic_turn_count >= 2:
            return True
        return False

    def should_end_conversation(self) -> bool:
        """
        Determine if conversation should end

        Returns:
            True if conversation should end
        """
        # Check manual stop
        if self.should_stop:
            return True

        # Check max turns
        if self.turn_count >= self.max_turns:
            return True

        # Check for natural ending signals with stricter criteria
        if len(self.messages) >= 10:  # allow enough back-and-forth before ending
            last_two = self.messages[-2:]
            last_texts = [m.content.lower() for m in last_two]
            doctor_last = next((m.content.lower() for m in reversed(self.messages) if m.role == "oncologist"), "")
            patient_last = next((m.content.lower() for m in reversed(self.messages) if m.role == "patient"), "")

            # Doctor uses an ending signal
            doctor_signaled = any(signal in doctor_last for signal in Settings.ENDING_SIGNALS)

            # Patient acknowledges closure
            patient_acks = [
                "no, that's all",
                "no that's all",
                "that's all",
                "no questions",
                "no more questions",
                "thank you",
                "thanks",
                "sounds good",
                "understood",
                "okay",
                "ok"
            ]
            patient_acknowledged = any(ack in patient_last for ack in patient_acks)

            if doctor_signaled and patient_acknowledged:
                return True

            # Fallback: both of the last two messages together contain a clear wrap-up
            combined_text = " ".join(last_texts)
            if doctor_signaled and any(ack in combined_text for ack in patient_acks):
                return True

        return False

    async def run_conversation(self) -> AsyncIterator[Message]:
        """
        Run the automatic conversation

        Yields:
            Message objects as they are generated
        """
        self.is_running = True
        self.should_stop = False

        try:
            # 1. Oncologist opens with introduction & results agenda item
            self.current_topic = "introduction"
            self.topic_turn_count = 0
            opening_msg = await self._generate_message(
                agent=self.oncologist,
                context=self.case_scenario,
                is_opening=True
            )
            self.topic_turn_count += 1
            self.doctor_agenda["introduction"] = True
            self.current_topic = self._get_next_topic()
            self.topic_turn_count = 0
            self.just_transitioned = False
            yield opening_msg

            # 2. Automatic back-and-forth until ending condition
            while not self.should_end_conversation():
                # Patient responds
                patient_msg = await self._generate_message(
                    agent=self.patient,
                    context=self.messages[-1].content if self.messages else "",
                    is_opening=False
                )
                yield patient_msg

                # Check if should stop after patient message
                if self.should_end_conversation():
                    break

                # Check if we should transition topics before oncologist responds
                if self._should_transition_topic() and self.current_topic:
                    # Mark current topic as complete and move to next
                    self.doctor_agenda[self.current_topic] = True
                    self.current_topic = self._get_next_topic()
                    self.topic_turn_count = 0
                    self.just_transitioned = True  # Set flag to force transition in prompt
                else:
                    self.just_transitioned = False

                # Oncologist responds
                oncologist_msg = await self._generate_message(
                    agent=self.oncologist,
                    context=self.messages[-1].content if self.messages else "",
                    is_opening=False
                )
                yield oncologist_msg
                
                # Clear transition flag after doctor responds
                self.just_transitioned = False

                # Update topic tracking after doctor message
                if self.current_topic:
                    self.topic_turn_count += 1
                    if self.current_topic == "closing":
                        if not self.doctor_agenda.get("closing", False) and self.topic_turn_count >= 1:
                            self.doctor_agenda["closing"] = True
                        if self.doctor_agenda.get("closing", False):
                            # Agenda complete
                            self.current_topic = None
                            self.topic_turn_count = 0
                else:
                    # All agenda items complete; no topic to track
                    self.topic_turn_count = 0

                self.turn_count += 1

        finally:
            self.is_running = False

    async def _generate_message(
        self,
        agent: BaseAgent,
        context: str,
        is_opening: bool
    ) -> Message:
        """
        Generate a single message from an agent

        Args:
            agent: Agent to generate message
            context: Context/prompt for the message
            is_opening: Whether this is the opening message

        Returns:
            Generated Message object
        """
        # Get conversation history in appropriate format
        history = self.get_conversation_history_for_llm(agent.get_role())

        # Compose coaching hint based on dialogue state
        def _build_context_hint(for_role: str) -> str:
            if for_role == "oncologist":
                # Get next priority topic
                next_priority = self._get_next_topic()
                topic_display_map = {
                    "introduction": "introduction & results",
                    "recommendation": "treatment recommendation",
                    "considerations": "practical considerations",
                    "closing": "closing notes"
                }
                topic_transition_map = {
                    "introduction": "share the key pathology and genomic results in plain language.",
                    "recommendation": "present your recommended plan for next steps and why it fits.",
                    "considerations": "outline practical considerations: side effects, logistics, timelines, and support.",
                    "closing": "summarize the plan, reinforce support, and set follow-up expectations."
                }
                topic_lead_map = {
                    "introduction": "deliver the main results in 2-3 sentences, reassure, and invite a quick reaction.",
                    "recommendation": "state your treatment recommendation, include the rationale, and check the patient's understanding.",
                    "considerations": "proactively cover logistics, timeline, side effects, and patient responsibilities in plain language.",
                    "closing": "summarize the plan, confirm next steps, reassure your availability, and invite any final questions."
                }
                remaining_labels = [
                    topic_display_map[t] for t in self.agenda_order if not self.doctor_agenda.get(t, False)
                ]
                remaining_str = ", ".join(remaining_labels) if remaining_labels else "(none)"
                concern_str = ", ".join(sorted(self.patient_concerns)) if self.patient_concerns else "(none)"

                # Check if we should transition topics (after 2-3 exchanges or if we just transitioned)
                should_transition = (self._should_transition_topic() or self.just_transitioned) and self.current_topic is not None
                active_topic = self.current_topic or next_priority
                
                # Opening-specific directive: greet briefly, then get to results and recommendation
                if is_opening:
                    opening_dir = (
                        "Brief greeting (1 sentence), then immediately cover the introduction & results agenda item."
                    )
                    reply_rule = opening_dir
                elif should_transition and next_priority:
                    # Force transition: acknowledge and move to next topic
                    topic_focus = topic_transition_map.get(next_priority, "cover the next important point.")
                    reply_rule = (
                        "Acknowledge the patient's question or worry in ONE short sentence, "
                        f"then pivot immediately to {topic_focus} "
                        "Do not continue elaborating on the previous topic beyond that single acknowledgement."
                    )
                elif self.last_question_by == "patient" and self.topic_turn_count < 2 and not self.just_transitioned and active_topic:
                    # Briefly answer, then re-lead the planned topic
                    topic_focus = topic_lead_map.get(active_topic, "return to the planned agenda item.")
                    reply_rule = (
                        "Respond to the patient's question in ONE short sentence, then "
                        f"{topic_focus}"
                    )
                else:
                    # Lead proactively to next topic
                    if active_topic and active_topic in topic_lead_map:
                        reply_rule = topic_lead_map[active_topic]
                    else:
                        reply_rule = "Respond directly to the patient's current point, reinforce support, and keep it concise."

                return (
                    f"Doctor agenda remaining: {remaining_str}. "
                    f"Known patient concerns: {concern_str}. "
                    f"{reply_rule} Keep 2-5 sentences, no lists."
                )
            else:
                concern_nudge = "If uncertain, ask one short follow-up question." if self.last_question_by != "patient" else "Answer the doctor's question directly."
                return (
                    f"Speak naturally. Keep 1-2 sentences. {concern_nudge} "
                    f"Stay consistent with your persona."
                )

        composed_context = f"{_build_context_hint(agent.get_role())}\n\n{context}"

        # Generate response
        full_response = ""
        async for chunk in agent.speak(
            context=composed_context,
            conversation_history=history if not is_opening else None,
            stream=True
        ):
            full_response += chunk

            # Call stream callback if provided
            if self.stream_callback:
                await self.stream_callback(agent.get_display_name(), chunk)

        # Simple response validator with one retry
        def _needs_revision(text: str) -> bool:
            stripped = text.strip()
            if not stripped:
                return True
            sentence_count = len([s for s in stripped.replace("\n", " ").split('.') if s.strip()])
            # Role-based sentence caps: doctors can elaborate more than patients
            max_sentences = 6 if agent.get_role() == "oncologist" else 3
            if sentence_count > max_sentences:
                return True
            # Allow slightly longer responses for doctors
            max_chars = 1200 if agent.get_role() == "oncologist" else 800
            if len(stripped) > max_chars:
                return True
            return False

        if _needs_revision(full_response):
            if agent.get_role() == "oncologist":
                revision_prompt = (
                    "Revise your previous answer to 2-5 concise sentences. "
                    "Respond directly to the last point. No lists, no headers."
                )
            else:
                revision_prompt = (
                    "Revise your previous answer to 1-3 short sentences. "
                    "Respond directly to the last point. No lists, no headers."
                )
            # Ask the agent to revise (non-streaming)
            revised = ""
            async for chunk in agent.speak(
                context=f"{_build_context_hint(agent.get_role())}\n\n{revision_prompt}",
                conversation_history=history if not is_opening else None,
                stream=False
            ):
                revised += chunk
            if revised.strip():
                full_response = revised

        # Create message object
        message = Message(
            speaker=agent.get_display_name(),
            role=agent.get_role(),
            content=full_response,
            model_info=agent.get_model_info()
        )

        # Update dialogue state and add to history
        self._update_state_from_message(message)
        self.messages.append(message)

        # TTS is now handled in the UI layer (app.py)

        return message

    def _update_state_from_message(self, message: Message) -> None:
        text = message.content.lower()

        # Track who asked the last question
        if "?" in text:
            self.last_question_by = message.role

        if message.role != "oncologist":
            # Collect patient concerns keywords
            concern_keywords = [
                ("chemo", "chemotherapy"),
                ("hair", "hair loss"),
                ("side effect", "side effects"),
                ("trial", "clinical trial"),
                ("test", "genomic testing"),
                ("come back", "recurrence"),
                ("work", "work impact"),
                ("cost", "cost"),
                ("scared", "fear")
            ]
            for key, label in concern_keywords:
                if key in text:
                    self.patient_concerns.add(label)

    def stop(self):
        """Stop the conversation"""
        self.should_stop = True

    def pause(self):
        """Pause the conversation"""
        self.is_paused = True

    def resume(self):
        """Resume the conversation"""
        self.is_paused = False

    async def _pausable_sleep(self, duration: float):
        """
        Sleep for duration seconds, but check for pause state every 0.1 seconds

        Args:
            duration: Sleep duration in seconds
        """
        elapsed = 0.0
        check_interval = 0.1

        while elapsed < duration:
            if self.should_stop:
                return

            # Check pause state from session_state if available
            is_paused = self.session_state.is_paused if self.session_state and hasattr(self.session_state, 'is_paused') else self.is_paused

            # While paused, wait in small increments
            while is_paused:
                await asyncio.sleep(0.1)
                if self.should_stop:
                    return
                # Re-check pause state
                is_paused = self.session_state.is_paused if self.session_state and hasattr(self.session_state, 'is_paused') else self.is_paused

            # Sleep for check_interval or remaining time, whichever is shorter
            sleep_time = min(check_interval, duration - elapsed)
            await asyncio.sleep(sleep_time)
            elapsed += sleep_time

    def get_messages(self) -> List[Message]:
        """Get all messages"""
        return self.messages

    def get_conversation_text(self) -> str:
        """Get full conversation as formatted text"""
        lines = ["=" * 80]
        lines.append("MEDICAL VISIT SIMULATION")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Oncologist: {self.oncologist.get_display_name()} ({self.oncologist.get_model_info()})")
        lines.append(f"Patient: {self.patient.get_display_name()} ({self.patient.get_model_info()})")
        lines.append("")
        lines.append("=" * 80)
        lines.append("")

        for msg in self.messages:
            lines.append(f"{msg.speaker}:")
            lines.append("-" * 40)
            lines.append(msg.content)
            lines.append("")
            lines.append("")

        return "\n".join(lines)

    def get_statistics(self) -> Dict:
        """Get conversation statistics"""
        return {
            "total_messages": len(self.messages),
            "oncologist_messages": len([m for m in self.messages if m.role == "oncologist"]),
            "patient_messages": len([m for m in self.messages if m.role == "patient"]),
            "turn_count": self.turn_count,
            "oncologist_name": self.oncologist.get_display_name(),
            "patient_name": self.patient.get_display_name(),
            "oncologist_model": self.oncologist.get_model_info(),
            "patient_model": self.patient.get_model_info()
        }
