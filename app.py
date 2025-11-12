"""
Medical Visit Simulator - Main Streamlit Application
An interactive web app simulating oncologist-patient consultations
"""
import streamlit as st
import asyncio
from datetime import datetime

# Import agents
from agents.oncologist_agents import ConservativeOncologist, LiberalOncologist
from agents.patient_agents import DoMorePatient, DoLessPatient

# Import LLM providers (with optional imports for providers you don't have installed)
from llm_providers.gemini_provider import GeminiProvider

# Optional providers - only imported if packages are installed
try:
    from llm_providers.claude_provider import ClaudeProvider
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

try:
    from llm_providers.openai_provider import OpenAIProvider
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import simulation components
from simulation.case_library import case_library, CaseScenario
from simulation.conversation_manager import ConversationManager

# Import utilities
from utils.storage import storage
from utils.export import exporter

# Import config
from config.settings import Settings


# Page configuration
st.set_page_config(
    page_title="Medical Visit Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'conversation_manager' not in st.session_state:
        st.session_state.conversation_manager = None

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'is_running' not in st.session_state:
        st.session_state.is_running = False

    if 'simulation_complete' not in st.session_state:
        st.session_state.simulation_complete = False

    if 'is_paused' not in st.session_state:
        st.session_state.is_paused = False


def create_llm_provider(provider_type: str, model: str):
    """
    Create LLM provider instance

    Args:
        provider_type: Type of provider (claude, gemini, openai)
        model: Model name

    Returns:
        LLM provider instance or None
    """
    api_key = Settings.get_api_key(provider_type)

    if not api_key:
        st.error(f"No API key found for {provider_type}. Please set it in your .env file.")
        return None

    try:
        if provider_type.lower() in ["claude", "anthropic"]:
            if not CLAUDE_AVAILABLE:
                st.error(f"Claude provider not available. Install with: pip install anthropic")
                return None
            return ClaudeProvider(api_key=api_key, model=model)
        elif provider_type.lower() in ["gemini", "google"]:
            return GeminiProvider(api_key=api_key, model=model)
        elif provider_type.lower() == "openai":
            if not OPENAI_AVAILABLE:
                st.error(f"OpenAI provider not available. Install with: pip install openai")
                return None
            return OpenAIProvider(api_key=api_key, model=model)
        else:
            st.error(f"Unknown provider type: {provider_type}")
            return None
    except Exception as e:
        st.error(f"Error creating {provider_type} provider: {str(e)}")
        return None


def create_oncologist(oncologist_type: str, llm_provider):
    """Create oncologist agent"""
    if oncologist_type == "Conservative":
        return ConservativeOncologist(llm_provider=llm_provider)
    else:  # Liberal
        return LiberalOncologist(llm_provider=llm_provider)


def create_patient(patient_type: str, llm_provider):
    """Create patient agent"""
    if patient_type == "Do More":
        return DoMorePatient(llm_provider=llm_provider)
    else:  # Do Less
        return DoLessPatient(llm_provider=llm_provider)


def sidebar():
    """Render sidebar configuration"""
    st.sidebar.title("Simulation Configuration")

    # Oncologist selection
    st.sidebar.subheader("1. Select Oncologist")
    oncologist_type = st.sidebar.radio(
        "Oncologist Type:",
        ["Conservative", "Liberal"],
        help="Conservative: Guidelines-based. Liberal: Precision medicine-focused."
    )

    # Patient selection
    st.sidebar.subheader("2. Select Patient")
    patient_type = st.sidebar.radio(
        "Patient Type:",
        ["Do More", "Do Less"],
        help="Do More: Wants aggressive treatment. Do Less: Prefers minimal intervention."
    )

    st.sidebar.divider()

    # LLM Provider selection
    st.sidebar.subheader("3. Select AI Models")

    # Build list of available providers
    available_providers = ["Gemini"]  # Gemini is always available
    if CLAUDE_AVAILABLE:
        available_providers.insert(0, "Claude")
    if OPENAI_AVAILABLE:
        available_providers.append("OpenAI")

    # Show warning if only Gemini is available
    if len(available_providers) == 1:
        st.sidebar.warning("Only Gemini is available")

    # Oncologist model
    onc_provider = st.sidebar.selectbox(
        "Oncologist AI Provider:",
        available_providers,
        key="onc_provider"
    )

    onc_models = Settings.get_models_for_provider(onc_provider)
    onc_model = st.sidebar.selectbox(
        "Oncologist Model:",
        onc_models,
        key="onc_model"
    )

    # Patient model
    patient_provider = st.sidebar.selectbox(
        "Patient AI Provider:",
        available_providers,
        key="patient_provider"
    )

    patient_models = Settings.get_models_for_provider(patient_provider)
    patient_model = st.sidebar.selectbox(
        "Patient Model:",
        patient_models,
        key="patient_model"
    )

    st.sidebar.divider()

    # Case selection
    st.sidebar.subheader("4. Select Case")
    case_source = st.sidebar.radio(
        "Case Source:",
        ["Pre-defined", "Custom"],
        key="case_source"
    )

    case_scenario = None
    case_id = None
    case_title = None

    if case_source == "Pre-defined":
        case_titles = case_library.get_case_titles()
        selected_case_id = st.sidebar.selectbox(
            "Select Case:",
            list(case_titles.keys()),
            format_func=lambda x: case_titles[x],
            key="selected_case"
        )

        case_scenario_obj = case_library.get_case(selected_case_id)
        if case_scenario_obj:
            case_scenario = case_scenario_obj.format_for_prompt()
            case_id = selected_case_id
            case_title = case_scenario_obj.title

            with st.sidebar.expander("View Case Details"):
                st.text(case_scenario)
    else:
        case_scenario = st.sidebar.text_area(
            "Enter Case Details:",
            height=200,
            placeholder="Enter patient case details here...",
            key="custom_case"
        )
        case_title = "Custom Case"

    st.sidebar.divider()

    # Simulation settings
    st.sidebar.subheader("Settings")
    max_turns = st.sidebar.slider(
        "Max Conversation Turns:",
        min_value=5,
        max_value=50,
        value=Settings.DEFAULT_MAX_TURNS,
        help="Maximum number of back-and-forth exchanges"
    )

    temperature = st.sidebar.slider(
        "AI Temperature:",
        min_value=0.0,
        max_value=1.0,
        value=Settings.DEFAULT_TEMPERATURE,
        step=0.1,
        help="Higher = more creative, Lower = more focused"
    )

    st.sidebar.divider()

    # Text-to-Speech settings
    st.sidebar.subheader("Text-to-Speech")
    enable_tts = st.sidebar.checkbox(
        "Enable Voice",
        value=Settings.ENABLE_TTS,
        help="Play conversation with voice. Google Cloud TTS has different voices for doctor/patient at 1.5x speed."
    )

    tts_engine = Settings.TTS_ENGINE  # Default from settings
    if enable_tts:
        tts_engine = st.sidebar.selectbox(
            "TTS Engine:",
            ["gtts", "google_cloud"],
            index=0 if Settings.TTS_ENGINE == "gtts" else 1,
            format_func=lambda x: "gTTS (Basic, Works Immediately)" if x == "gtts" else "Google Cloud (Recommended, Free Tier)",
            help="gTTS works immediately but has basic quality. Google Cloud has realistic neural voices (1M chars/month free) but needs setup."
        )

        if tts_engine == "google_cloud" and not Settings.GOOGLE_CLOUD_CREDENTIALS:
            st.sidebar.info("ℹ️ Google Cloud TTS needs setup. See GOOGLE_CLOUD_TTS_SETUP.md for quick guide (5 min, free tier).")

    return {
        "oncologist_type": oncologist_type,
        "patient_type": patient_type,
        "onc_provider": onc_provider,
        "onc_model": onc_model,
        "patient_provider": patient_provider,
        "patient_model": patient_model,
        "case_scenario": case_scenario,
        "case_id": case_id,
        "case_title": case_title,
        "max_turns": max_turns,
        "temperature": temperature,
        "enable_tts": enable_tts,
        "tts_engine": tts_engine
    }


def initialize_conversation(config):
    """Initialize conversation manager and agents"""
    # Create LLM providers
    onc_provider = create_llm_provider(config["onc_provider"], config["onc_model"])
    patient_provider = create_llm_provider(config["patient_provider"], config["patient_model"])

    if not onc_provider or not patient_provider:
        st.error("Failed to initialize AI providers. Please check your API keys.")
        return None

    # Create agents
    oncologist = create_oncologist(config["oncologist_type"], onc_provider)
    patient = create_patient(config["patient_type"], patient_provider)

    # Update temperature
    oncologist.temperature = config["temperature"]
    patient.temperature = config["temperature"]

    # Create conversation manager with TTS enabled
    manager = ConversationManager(
        oncologist=oncologist,
        patient=patient,
        case_scenario=config["case_scenario"],
        max_turns=config["max_turns"],
        stream_callback=None,  # We'll handle display separately
        enable_tts=config.get("enable_tts", False),
        tts_engine=config.get("tts_engine", "gtts"),
        tts_container=None,  # Audio played in main UI
        session_state=st.session_state
    )

    return manager


def run_simulation_step(config):
    """Run one step of the simulation"""
    import time
    import asyncio

    if 'conversation_generator' not in st.session_state:
        # Initialize the conversation
        manager = initialize_conversation(config)
        if not manager:
            st.session_state.is_running = False
            return

        st.session_state.conversation_manager = manager
        st.session_state.conversation_generator = manager.run_conversation()
        st.session_state.messages = []
        st.session_state.last_message_time = 0
        st.session_state.pending_audio = None  # Track pending audio

    # If paused, don't proceed
    if st.session_state.is_paused:
        time.sleep(0.1)  # Small delay to prevent CPU spinning
        st.rerun()
        return

    # Check if we should wait between messages
    current_time = time.time()
    time_since_last = current_time - st.session_state.last_message_time
    if time_since_last < 20.0:  # 20 second delay between messages
        time.sleep(0.1)  # Small delay before rerun
        st.rerun()
        return

    # Try to get next message
    try:
        # Get the next message
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        message = loop.run_until_complete(
            st.session_state.conversation_generator.__anext__()
        )
        loop.close()

        # Add to messages
        st.session_state.messages.append(message.to_dict())
        st.session_state.last_message_time = current_time

        # Generate TTS if enabled (but don't play yet)
        if config.get("enable_tts", False) and st.session_state.conversation_manager.tts_manager:
            try:
                audio_bytes = st.session_state.conversation_manager.tts_manager.synthesize(
                    message.content,
                    message.role
                )
                if audio_bytes:
                    # Store audio to play on next render
                    st.session_state.pending_audio = audio_bytes
            except Exception as e:
                st.warning(f"TTS generation failed: {str(e)}")

        # Rerun to display new message and play audio
        st.rerun()

    except StopAsyncIteration:
        # Conversation complete
        st.session_state.simulation_complete = True
        st.session_state.is_running = False
        if 'conversation_generator' in st.session_state:
            del st.session_state.conversation_generator
        st.success("Simulation completed!")


def main():
    """Main application"""
    initialize_session_state()

    # Title
    st.title("Medical Visit Simulator")
    st.markdown("*AI-powered simulation of oncologist-patient consultations*")

    # Sidebar configuration
    config = sidebar()

    # Main content area
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        start_disabled = (
            st.session_state.is_running or
            not config["case_scenario"] or
            config["case_scenario"].strip() == ""
        )

        if st.button(
            "Start Simulation",
            disabled=start_disabled,
            use_container_width=True,
            type="primary"
        ):
            st.session_state.is_running = True
            st.session_state.simulation_complete = False
            st.session_state.is_paused = False
            st.session_state.messages = []
            # Clean up any existing generator and timing
            if 'conversation_generator' in st.session_state:
                del st.session_state.conversation_generator
            if 'last_message_time' in st.session_state:
                del st.session_state.last_message_time
            if 'conversation_manager' in st.session_state:
                del st.session_state.conversation_manager
            if 'pending_audio' in st.session_state:
                del st.session_state.pending_audio
            st.rerun()

    with col2:
        pause_disabled = not st.session_state.is_running or st.session_state.simulation_complete
        pause_label = "Resume" if st.session_state.is_paused else "Pause"

        if st.button(
            pause_label,
            disabled=pause_disabled,
            use_container_width=True,
            key="pause_button"
        ):
            st.session_state.is_paused = not st.session_state.is_paused
            # The running simulation will detect this change on next iteration

    with col3:
        if st.button(
            "Stop",
            disabled=not st.session_state.is_running,
            use_container_width=True
        ):
            if st.session_state.conversation_manager:
                st.session_state.conversation_manager.stop()
            st.session_state.is_running = False
            st.session_state.is_paused = False
            # Clean up generator and audio
            if 'conversation_generator' in st.session_state:
                del st.session_state.conversation_generator
            if 'pending_audio' in st.session_state:
                del st.session_state.pending_audio
            st.rerun()

    with col4:
        save_disabled = len(st.session_state.messages) == 0

        if st.button(
            "Save",
            disabled=save_disabled,
            use_container_width=True
        ):
            # Save conversation
            if st.session_state.conversation_manager:
                stats = st.session_state.conversation_manager.get_statistics()

                conversation_id = storage.save_conversation(
                    messages=st.session_state.messages,
                    oncologist_type=config["oncologist_type"],
                    patient_type=config["patient_type"],
                    oncologist_model=config["onc_model"],
                    patient_model=config["patient_model"],
                    case_id=config["case_id"],
                    case_title=config["case_title"],
                    statistics=stats
                )

                st.success(f"Conversation saved! (ID: {conversation_id})")

    with col5:
        export_disabled = len(st.session_state.messages) == 0

        if st.button(
            "Export",
            disabled=export_disabled,
            use_container_width=True
        ):
            st.session_state.show_export_options = True

    # Export options
    if hasattr(st.session_state, 'show_export_options') and st.session_state.show_export_options:
        with st.expander("Export Options", expanded=True):
            export_col1, export_col2, export_col3 = st.columns(3)

            metadata = {
                "timestamp": datetime.now().isoformat(),
                "oncologist_type": config["oncologist_type"],
                "patient_type": config["patient_type"],
                "oncologist_model": config["onc_model"],
                "patient_model": config["patient_model"],
                "case_title": config["case_title"],
                "oncologist_name": st.session_state.messages[0]["speaker"] if st.session_state.messages else "N/A",
                "patient_name": st.session_state.messages[1]["speaker"] if len(st.session_state.messages) > 1 else "N/A"
            }

            with export_col1:
                if st.button("Export as PDF", use_container_width=True):
                    try:
                        filepath = exporter.export_to_pdf(st.session_state.messages, metadata)
                        st.success(f"Exported to: {filepath}")
                    except Exception as e:
                        st.error(f"Export failed: {str(e)}")

            with export_col2:
                if st.button("Export as Text", use_container_width=True):
                    try:
                        filepath = exporter.export_to_text(st.session_state.messages, metadata)
                        st.success(f"Exported to: {filepath}")
                    except Exception as e:
                        st.error(f"Export failed: {str(e)}")

            with export_col3:
                if st.button("Export as JSON", use_container_width=True):
                    try:
                        filepath = exporter.export_to_json(st.session_state.messages, metadata)
                        st.success(f"Exported to: {filepath}")
                    except Exception as e:
                        st.error(f"Export failed: {str(e)}")

    st.divider()

    # Show pause status
    if st.session_state.is_paused:
        st.info("⏸️ Simulation paused. Click Resume to continue.")

    # Display conversation messages (always show if we have any)
    if st.session_state.messages:
        st.subheader("Conversation")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(f"**{msg['speaker']}**")
                st.write(msg["content"])

        # Show statistics if simulation is complete
        if st.session_state.simulation_complete and st.session_state.conversation_manager:
            stats = st.session_state.conversation_manager.get_statistics()

            st.divider()
            st.subheader("Conversation Statistics")

            stat_col1, stat_col2, stat_col3 = st.columns(3)
            with stat_col1:
                st.metric("Total Messages", stats["total_messages"])
            with stat_col2:
                st.metric("Oncologist Messages", stats["oncologist_messages"])
            with stat_col3:
                st.metric("Patient Messages", stats["patient_messages"])

    # Play pending audio if available
    if 'pending_audio' in st.session_state and st.session_state.pending_audio:
        st.audio(st.session_state.pending_audio, format="audio/mp3", autoplay=True)
        st.session_state.pending_audio = None  # Clear after playing

    # Run simulation step if active
    if st.session_state.is_running:
        # Run one step of the simulation
        run_simulation_step(config)

    # Show welcome message if no messages
    if not st.session_state.messages and not st.session_state.is_running:
        # Welcome message
        st.info("""
        **Welcome to the Medical Visit Simulator!**

        This application simulates realistic oncologist-patient consultations using AI.

        **How to use:**
        1. Configure your simulation using the sidebar on the left
        2. Select oncologist and patient types
        3. Choose AI models for each role
        4. Select or enter a case scenario
        5. Click "Start Simulation" to begin
        6. Watch the conversation unfold automatically
        7. Save or export the conversation when complete

        **Agent Types:**
        - **Conservative Oncologist**: Follows guidelines strictly, evidence-based
        - **Liberal Oncologist**: Precision medicine-focused, considers trials
        - **Do-More Patient**: Wants aggressive treatment, proactive
        - **Do-Less Patient**: Prefers minimal intervention, quality-of-life focused
        """)


if __name__ == "__main__":
    main()
