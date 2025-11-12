# 🏥 Medical Visit Simulator

An interactive web application that simulates realistic oncologist-patient consultations using AI. The system creates autonomous conversations between different oncologist and patient personas to demonstrate various clinical decision-making styles and communication patterns.

## 🎯 Purpose

This simulator is designed for:
- **Medical education**: Demonstrating different communication styles and treatment philosophies
- **Case study analysis**: Exploring how different approaches affect patient discussions
- **Research**: Studying patterns in clinical communication and decision-making
- **Training**: Helping medical students and residents understand patient perspectives

## ✨ Features

### Four AI Personas

**Oncologists:**
1. **Conservative Oncologist** (Dr. Anderson)
   - Guidelines-based approach
   - Evidence-focused, risk-averse
   - Follows NCCN/ASCO guidelines strictly
   - Prefers FDA-approved treatments

2. **Liberal Oncologist** (Dr. Chen)
   - Precision medicine-focused
   - Considers investigational therapies
   - Enthusiastic about genomic testing
   - Presents clinical trial options

**Patients:**
1. **Do-More Patient** (Sarah)
   - Wants aggressive treatment
   - Proactive and research-oriented
   - Willing to tolerate side effects
   - Asks about all available options

2. **Do-Less Patient** (Linda)
   - Prefers minimal intervention
   - Quality-of-life focused
   - Anxious about side effects
   - Seeks reassurance about conservative approaches

### Key Capabilities

- ✅ **Autonomous conversations**: AI agents converse automatically with 2-second pauses between messages
- ✅ **Multiple LLM support**: Use Claude, Gemini, or OpenAI for each role
- ✅ **Pre-defined cases**: 5 realistic breast cancer case scenarios
- ✅ **Custom cases**: Enter your own case details
- ✅ **Real-time streaming**: Watch conversations unfold in real-time
- ✅ **Text-to-Speech**: Voice playback with different voices for doctor/patient (1.5x speed)
- ✅ **Pause/Resume**: Control conversation flow at any time
- ✅ **Save conversations**: Store simulations in local database
- ✅ **Export options**: Export to PDF, Text, or JSON
- ✅ **Configurable settings**: Adjust conversation length, AI temperature, etc.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- API keys for at least one LLM provider (Claude, Gemini, or OpenAI)

### Installation

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your API keys:
   ```
   ANTHROPIC_API_KEY=your_key_here
   GOOGLE_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   The app will automatically open at `http://localhost:8501`

## 📖 Usage Guide

### Running a Simulation

1. **Configure the simulation** (left sidebar):
   - Select oncologist type (Conservative or Liberal)
   - Select patient type (Do More or Do Less)
   - Choose AI models for each role
   - Select a pre-defined case or enter custom case details
   - Adjust settings (max turns, temperature)

2. **Start the simulation**:
   - Click "▶️ Start Simulation"
   - Watch the conversation unfold automatically
   - The oncologist will open with case review
   - Patient and oncologist will alternate responses

3. **Manage the conversation**:
   - Click "⏸️ Pause" to pause the simulation, "▶️ Resume" to continue
   - Click "⏹️ Stop" to halt the simulation early
   - Click "💾 Save" to store the conversation
   - Click "📥 Export" to download as PDF, Text, or JSON

### Text-to-Speech

The simulator includes voice playback with distinct voices at 1.5x speed.

**Recommended: Google Cloud TTS (FREE TIER)**:
- **Realistic neural voices** with male/female differentiation
- **Free tier**: 1 million characters per month (plenty for most use)
- Doctor: Male neural voice
- Patient: Female neural voice
- **Quick setup** (5 minutes):
  1. Create free Google Cloud account at https://console.cloud.google.com/
  2. Enable Text-to-Speech API
  3. Create service account and download JSON credentials
  4. Set path in `.env` file (see `.env.example` for detailed steps)

**Alternative: gTTS (Basic)**:
- Simple free option, no setup
- Same voice for both speakers (lower quality)
- Good for testing, but Google Cloud TTS strongly recommended

**Controls**:
- Enable/disable voice in sidebar
- Select TTS engine (Google Cloud or gTTS)
- Pause button also pauses audio playback

### Pre-defined Cases

The simulator includes 5 realistic breast cancer cases:

1. **Early-stage ER+ Breast Cancer**
   - Stage IIA, Oncotype DX 22 (intermediate)
   - Classic case for chemotherapy decision-making

2. **Triple-Negative Breast Cancer**
   - Stage IIIA, post-neoadjuvant setting
   - Residual disease after chemo + immunotherapy

3. **HER2-Positive Breast Cancer**
   - Stage IIB, newly diagnosed
   - Treatment planning for HER2-targeted therapy

4. **Metastatic ER+ Breast Cancer**
   - De novo Stage IV with bone and liver mets
   - First-line treatment decisions

5. **Borderline Chemotherapy Indication**
   - Oncotype DX 18, older patient with comorbidities
   - Uncertainty about chemotherapy benefit

### Understanding the Combinations

You can create **4 different simulation combinations**:

| Oncologist | Patient | Expected Dynamic |
|------------|---------|------------------|
| Conservative | Do More | Patient pushes for more; doctor reassures standard is enough |
| Conservative | Do Less | Alignment on conservative approach; gentle encouragement |
| Liberal | Do More | Alignment on aggressive approach; discussion of trials |
| Liberal | Do Less | Doctor presents options; patient needs reassurance about necessity |

## 🏗️ Architecture

```
medical_visit_simulator/
├── app.py                      # Main Streamlit application
├── agents/                     # Agent definitions
│   ├── base_agent.py          # Base agent class
│   ├── oncologist_agents.py   # Conservative & Liberal oncologists
│   └── patient_agents.py      # Do-more & Do-less patients
├── llm_providers/             # LLM API integrations
│   ├── base_provider.py       # Abstract provider interface
│   ├── claude_provider.py     # Anthropic Claude
│   ├── gemini_provider.py     # Google Gemini
│   └── openai_provider.py     # OpenAI GPT
├── simulation/                # Conversation logic
│   ├── conversation_manager.py # Auto turn-taking orchestration
│   └── case_library.py        # Pre-defined cases
├── utils/                     # Utilities
│   ├── export.py              # PDF/Text/JSON export
│   ├── storage.py             # SQLite database storage
│   └── tts_manager.py         # Text-to-speech with voice differentiation
└── config/                    # Configuration
    └── settings.py            # App settings and defaults
```

### Key Components

**Agents** (`agents/`):
- Each agent has a detailed system prompt defining personality, medical knowledge, and communication style
- Agents use the LLM provider to generate responses
- `BaseAgent` provides common interface

**LLM Providers** (`llm_providers/`):
- Abstract interface allows swapping between Claude, Gemini, OpenAI
- Handles API calls, streaming, and error handling
- Each provider adapts to its specific API format

**Conversation Manager** (`simulation/conversation_manager.py`):
- Orchestrates automatic turn-taking
- Maintains conversation history
- Detects natural ending points
- Formats messages for LLM APIs

**Storage & Export** (`utils/`):
- SQLite database for saving conversations
- Export to PDF (formatted), Text (plain), or JSON (structured)
- Query and retrieve past simulations

**Text-to-Speech** (`utils/tts_manager.py`):
- Supports Google Cloud TTS (recommended, free tier) and gTTS (basic)
- Google Cloud: Realistic neural voices with male/female differentiation
- gTTS: Simple fallback option (same voice for all)
- 1.5x speed playback for Google Cloud TTS
- Pause-aware audio playback (respects pause button)

## 🔧 Configuration

### Settings (`config/settings.py`)

Key configurable parameters:

- `DEFAULT_MAX_TURNS`: Maximum conversation exchanges (default: 20)
- `DEFAULT_TEMPERATURE`: AI creativity level (default: 0.7)
- `DEFAULT_MAX_TOKENS`: Maximum response length (default: 1000)
- `ENDING_SIGNALS`: Phrases that indicate conversation conclusion

### Environment Variables (`.env`)

Required API keys:
- `ANTHROPIC_API_KEY`: For Claude models
- `GOOGLE_API_KEY`: For Gemini models
- `OPENAI_API_KEY`: For GPT models

Text-to-Speech settings:
- `ENABLE_TTS`: Enable/disable voice playback (default: true)
- `TTS_ENGINE`: "gtts" (free) or "google_cloud" (premium)
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google Cloud credentials (optional)

You only need keys for the providers you plan to use.

## 📊 Data Management

### Saved Conversations

Conversations are saved to `data/conversations.db` (SQLite database).

Each saved conversation includes:
- Timestamp
- Oncologist and patient types
- LLM models used
- Case information
- Full conversation transcript
- Statistics (message counts, turn count)

### Exports

Exported files are saved to `exports/` directory:
- **PDF**: Formatted document with metadata and conversation
- **Text**: Plain text transcript
- **JSON**: Structured data for analysis

## 🎓 Educational Use Cases

### For Medical Students

- **Communication styles**: Compare how different oncologists present the same information
- **Shared decision-making**: Observe how doctors handle different patient preferences
- **Evidence vs. innovation**: Understand tension between guidelines and emerging treatments

### For Researchers

- **Pattern analysis**: Export JSON data to analyze conversation patterns
- **Decision variation**: Study how persona combinations affect treatment discussions
- **Communication effectiveness**: Compare approaches across multiple simulations

### For Patients & Advocates

- **Perspective understanding**: See consultations from both sides
- **Question preparation**: Learn what questions to ask oncologists
- **Treatment philosophy**: Understand different oncology practice styles

## ⚠️ Important Disclaimers

- **Not for clinical use**: This is an educational simulation only
- **AI limitations**: Responses are generated by AI and may contain inaccuracies
- **Medical advice**: Do not use this tool for actual medical decision-making
- **Verification**: All medical information should be verified with healthcare professionals

## 🛠️ Troubleshooting

### API Key Issues

**Problem**: "No API key found for [provider]"
**Solution**: Check that your `.env` file exists and contains valid API keys

### Import Errors

**Problem**: "ModuleNotFoundError"
**Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

### Streaming Issues

**Problem**: Conversation not appearing in real-time
**Solution**: This is expected with Streamlit's async handling. Messages appear when complete.

### Database Errors

**Problem**: "Unable to open database"
**Solution**: Ensure `data/` directory exists and is writable

### Text-to-Speech Issues

**Problem**: "No module named 'google.cloud.texttospeech'" or TTS not working
**Solution**:
1. Install: `pip install google-cloud-texttospeech gtts`
2. Set up Google Cloud credentials (see `.env.example` for step-by-step)
3. Or temporarily use gTTS by changing `TTS_ENGINE=gtts` in `.env`

**Problem**: Google Cloud TTS setup seems complicated
**Solution**: It's actually quick! Follow these steps:
1. Go to https://console.cloud.google.com/ (free account)
2. Create new project
3. Enable Text-to-Speech API (just click enable)
4. Create service account (IAM > Service Accounts > Create)
5. Download JSON key file
6. Set path in `.env`: `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`
7. Done! You get 1 million free characters per month

**Problem**: TTS sounds robotic or unrealistic
**Solution**: Make sure you're using Google Cloud TTS, not gTTS. Check your `.env` has `TTS_ENGINE=google_cloud`

## 🔮 Future Enhancements

Completed:
- [x] Voice mode with text-to-speech (with voice differentiation and pause support)

Potential additions:
- [ ] Multi-specialty support (lung, colon, etc.)
- [ ] Side-by-side comparison of multiple simulations
- [ ] Analytics dashboard for conversation patterns
- [ ] Intervention mode (inject prompts mid-conversation)
- [ ] Evaluation metrics vs. clinical guidelines

## 📝 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [Anthropic Claude](https://www.anthropic.com/) - AI model
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI model
- [OpenAI GPT](https://openai.com/) - AI model

## 📧 Support

For issues or questions:
1. Check this README for troubleshooting
2. Review the code comments for implementation details
3. Ensure all dependencies and API keys are correctly configured

---

**Made for medical education and research** | **Not for clinical use**
