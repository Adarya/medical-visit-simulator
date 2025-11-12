# 🚀 Quick Start Guide

Get your Medical Visit Simulator up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up API Keys

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add at least one API key:
   ```bash
   # For Claude (recommended):
   ANTHROPIC_API_KEY=sk-ant-xxxxx

   # OR for Gemini:
   GOOGLE_API_KEY=xxxxx

   # OR for OpenAI:
   OPENAI_API_KEY=sk-xxxxx
   ```

### Where to Get API Keys

- **Claude (Anthropic)**: https://console.anthropic.com/
- **Gemini (Google)**: https://makersuite.google.com/app/apikey
- **OpenAI**: https://platform.openai.com/api-keys

## Step 3: Run the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Step 4: Run Your First Simulation

1. **Left Sidebar - Configure**:
   - Select "Liberal" oncologist
   - Select "Do More" patient
   - Choose Claude or Gemini for both roles
   - Select "Case 1: Early-stage ER+ Breast Cancer"

2. **Main Area - Start**:
   - Click "▶️ Start Simulation"
   - Watch the conversation unfold!

3. **After Completion**:
   - Click "💾 Save" to store the conversation
   - Click "📥 Export" to download as PDF

## Try Different Combinations

Experiment with all 4 persona combinations:

| # | Oncologist | Patient | What to Expect |
|---|------------|---------|----------------|
| 1 | Conservative | Do More | Patient wants more; doctor reassures standard care is sufficient |
| 2 | Conservative | Do Less | Both align on conservative approach |
| 3 | Liberal | Do More | Both align on aggressive/innovative approach |
| 4 | Liberal | Do Less | Doctor presents options; patient hesitant |

## Troubleshooting

**"No API key found"**
→ Check your `.env` file exists and has valid keys

**"Module not found"**
→ Run `pip install -r requirements.txt`

**Conversation not streaming**
→ This is normal - full messages appear when complete

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore all 5 pre-defined cases
- Try creating custom cases
- Export conversations for analysis
- Experiment with different AI models and temperatures

---

**Enjoy exploring different clinical communication styles!**
