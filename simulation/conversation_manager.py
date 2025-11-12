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
        self.doctor_agenda = {
            "rapport": False,
            "results_summary": False,
            "plan": False,
            "side_effects": False,
            "preferences": False,
            "follow_up": False
        }
        self.patient_concerns = set()  # keywords gathered from patient turns
        self.last_question_by: Optional[str] = None  # "oncologist" or "patient"
        
        # Topic turn tracking for doctor-led conversation flow
        self.current_topic: Optional[str] = None  # Current agenda item being discussed
        self.topic_turn_count: int = 0  # Number of exchanges on current topic

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
        priority_order = [
            "results_summary",
            "plan",
            "preferences",
            "side_effects",
            "follow_up",
            "rapport"
        ]
        remaining = [k for k, v in self.doctor_agenda.items() if not v]
        return next((p for p in priority_order if p in remaining), None)

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
            # 1. Oncologist opens with case review and initial assessment
            opening_msg = await self._generate_message(
                agent=self.oncologist,
                context=self.case_scenario,
                is_opening=True
            )
            # Detect initial topic from opening message
            opening_text = opening_msg.content.lower()
            if any(k in opening_text for k in ["result", "results", "margins", "nodes", "pathology", "scan", "imaging", "biopsy"]):
                self.current_topic = "results_summary"
            elif any(k in opening_text for k in ["plan", "treatment", "recommend", "therapy", "chemotherapy", "surgery"]):
                self.current_topic = "plan"
            else:
                # Default to results_summary as it's typically first
                self.current_topic = "results_summary"
            self.topic_turn_count = 0
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

                # Oncologist responds
                oncologist_msg = await self._generate_message(
                    agent=self.oncologist,
                    context=self.messages[-1].content if self.messages else "",
                    is_opening=False
                )
                yield oncologist_msg

                # Update topic tracking after doctor message
                # Detect which topic the doctor actually covered based on agenda updates
                # Check which topics were just marked as complete or mentioned
                doctor_text = oncologist_msg.content.lower()
                
                # Determine current topic from doctor's message
                detected_topic = None
                if any(k in doctor_text for k in ["result", "results", "margins", "nodes", "pathology", "scan", "imaging", "biopsy"]):
                    detected_topic = "results_summary"
                elif any(k in doctor_text for k in ["plan", "treatment", "recommend", "therapy", "chemotherapy", "surgery"]):
                    detected_topic = "plan"
                elif any(k in doctor_text for k in ["preference", "what matters", "how do you feel", "your concerns", "your values"]):
                    detected_topic = "preferences"
                elif any(k in doctor_text for k in ["side effect", "side effects", "nausea", "fatigue", "hair", "risk", "risks"]):
                    detected_topic = "side_effects"
                elif any(k in doctor_text for k in ["follow", "follow-up", "next appointment", "schedule", "come back"]):
                    detected_topic = "follow_up"
                elif any(k in doctor_text for k in ["hi", "hello", "how are you", "good to see you"]):
                    detected_topic = "rapport"
                
                # Update current topic and turn count
                if detected_topic and detected_topic != self.current_topic:
                    # Topic changed
                    self.current_topic = detected_topic
                    self.topic_turn_count = 1
                elif self.current_topic:
                    # Same topic, increment counter
                    self.topic_turn_count += 1
                elif not self.current_topic:
                    # No current topic, use next priority
                    self.current_topic = self._get_next_topic()
                    self.topic_turn_count = 1

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
                remaining = [k for k, v in self.doctor_agenda.items() if not v]
                remaining_str = ", ".join(remaining) if remaining else "(none)"
                concern_str = ", ".join(sorted(self.patient_concerns)) if self.patient_concerns else "(none)"

                # Check if we should transition topics (after 2-3 exchanges)
                should_transition = self._should_transition_topic() and self.current_topic is not None
                
                # Opening-specific directive: greet briefly, then get to results and recommendation
                if is_opening:
                    opening_dir = (
                        "Brief greeting (1 sentence), then immediately summarize key results "
                        "and give your initial recommendation in plain language."
                    )
                    reply_rule = opening_dir
                elif should_transition and next_priority:
                    # Force transition: acknowledge and move to next topic
                    transition_phrases = [
                        "We can discuss that more later, but let me also cover",
                        "That's a good point. I also want to make sure we cover",
                        "I understand your concern. Let me also mention",
                        "We can come back to that. Another important thing is"
                    ]
                    transition_base = transition_phrases[0]  # Use first one as default
                    
                    if next_priority == "results_summary":
                        transition_dir = f"{transition_base} your test results."
                    elif next_priority == "plan":
                        transition_dir = f"{transition_base} the treatment plan I'm recommending."
                    elif next_priority == "preferences":
                        transition_dir = f"{transition_base} what matters most to you in this decision."
                    elif next_priority == "side_effects":
                        transition_dir = f"{transition_base} potential side effects."
                    elif next_priority == "follow_up":
                        transition_dir = f"{transition_base} our follow-up plan."
                    else:
                        transition_dir = f"{transition_base} the next important point."
                    
                    reply_rule = transition_dir
                elif self.last_question_by == "patient" and self.topic_turn_count < 2:
                    # Answer questions directly only if we haven't exceeded turn limit
                    reply_rule = "Answer the patient's last question directly."
                else:
                    # Lead proactively to next topic
                    if next_priority == "results_summary":
                        reply_rule = "Provide a concise results summary now."
                    elif next_priority == "plan":
                        reply_rule = "State your clear recommendation now, including rationale in 1-2 sentences."
                    elif next_priority == "preferences":
                        reply_rule = "Briefly check the patient's preferences or concerns."
                    elif next_priority == "side_effects":
                        reply_rule = "Mention the top 1-2 side effects most relevant here."
                    elif next_priority == "follow_up":
                        reply_rule = "Address follow-up or next steps briefly."
                    else:
                        reply_rule = "Offer the next point clearly, then pause."

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

        if message.role == "oncologist":
            # Improved heuristic agenda completion with expanded keywords
            # Rapport - greeting and connection
            if any(k in text for k in ["hi", "hello", "how are you", "good to see you", "nice to meet", "welcome"]):
                self.doctor_agenda["rapport"] = True
            
            # Results summary - test results, pathology, imaging
            if any(k in text for k in [
                "result", "results", "margins", "nodes", "pathology", "pathological", 
                "scan", "imaging", "biopsy", "tumor size", "grade", "stage",
                "clear margins", "lymph nodes", "cancer cells", "test shows"
            ]):
                self.doctor_agenda["results_summary"] = True
            
            # Plan - treatment recommendation
            if any(k in text for k in [
                "plan", "treatment", "we'll do", "recommend", "recommendation",
                "i suggest", "i'd recommend", "we should", "going to do",
                "therapy", "chemotherapy", "surgery", "radiation"
            ]):
                self.doctor_agenda["plan"] = True
            
            # Side effects - risks and side effects
            if any(k in text for k in [
                "side effect", "side effects", "nausea", "fatigue", "hair", "hair loss",
                "risk", "risks", "complications", "adverse", "tolerate",
                "may cause", "could cause", "common side"
            ]):
                self.doctor_agenda["side_effects"] = True
            
            # Preferences - patient values and concerns
            if any(k in text for k in [
                "preference", "preferences", "what matters", "how do you feel", 
                "what do you think", "your concerns", "your values",
                "important to you", "your goals", "your priorities"
            ]):
                self.doctor_agenda["preferences"] = True
            
            # Follow-up - next steps and scheduling
            if any(k in text for k in [
                "follow", "follow-up", "follow up", "see you", "next appointment",
                "schedule", "scheduling", "come back", "return", "check back",
                "monitoring", "surveillance", "next visit"
            ]):
                self.doctor_agenda["follow_up"] = True
            
            # Track topic transitions explicitly
            # If doctor mentions moving on or transitioning, mark current topic as complete
            if any(k in text for k in ["let me also", "another thing", "also important", "i also want", "let's also"]):
                # If we're on a topic, mark it complete when transitioning
                if self.current_topic and self.current_topic in self.doctor_agenda:
                    self.doctor_agenda[self.current_topic] = True
        else:
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
