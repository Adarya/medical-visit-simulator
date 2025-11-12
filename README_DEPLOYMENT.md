# Deployment Guide - Medical Visit Simulator

Complete guide to deploying your Medical Visit Simulator to Streamlit Community Cloud (free).

## 🎯 Quick Start

**Total Time**: ~1 hour
**Cost**: $0 (completely free)
**Platform**: Streamlit Community Cloud

---

## 📋 Prerequisites

Before deploying, ensure you have:

1. **GitHub Account** - Free at https://github.com/join
2. **API Keys** - At least one of:
   - Google Gemini API key (recommended for free tier)
   - Anthropic Claude API key
   - OpenAI API key
3. **Your code** - This repository ready to push

---

## 🚀 Step-by-Step Deployment

### Phase 1: Prepare Your Repository (10 minutes)

#### 1.1 Initialize Git (if not already done)

```bash
cd /Users/adary/Documents/ai_in_oncology_unit/medical_visit_simulator
git init
```

#### 1.2 Configure Your Local Secrets (Optional - for local testing)

1. Open `.streamlit/secrets.toml`
2. Replace placeholder values with your actual API keys:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   GOOGLE_API_KEY = "AIza..."
   OPENAI_API_KEY = "sk-..."
   ```
3. Save the file
4. **IMPORTANT**: This file is already in `.gitignore` and will NOT be committed

#### 1.3 Commit Your Code

```bash
git add .
git commit -m "Initial commit: Medical Visit Simulator"
```

#### 1.4 Create GitHub Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `medical-visit-simulator`
   - **Description**: "AI-powered medical visit simulator for oncology education"
   - **Visibility**: Choose Public or Private (both work with Streamlit Cloud)
   - **DO NOT** initialize with README, license, or .gitignore (you already have these)
3. Click **"Create repository"**

#### 1.5 Push to GitHub

GitHub will show you commands. Copy and run them:

```bash
git remote add origin https://github.com/YOUR_USERNAME/medical-visit-simulator.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

---

### Phase 2: Deploy to Streamlit Community Cloud (10 minutes)

#### 2.1 Sign Up for Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click **"Sign up"**
3. Click **"Continue with GitHub"**
4. Authorize Streamlit to access your GitHub repositories
5. You'll be redirected to your Streamlit Cloud dashboard

#### 2.2 Deploy Your App

1. Click **"New app"** button (top right)
2. Fill in the deployment form:
   - **Repository**: Select `YOUR_USERNAME/medical-visit-simulator`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (optional): Choose a custom subdomain or leave default

3. Click **"Advanced settings..."** to expand the secrets section

#### 2.3 Configure Secrets (CRITICAL STEP!)

In the **"Secrets"** text box, paste your configuration:

**For Gemini-only (simplest)**:
```toml
GOOGLE_API_KEY = "AIzaSy..."
ENABLE_TTS = "true"
TTS_ENGINE = "gtts"
```

**For All Providers**:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
GOOGLE_API_KEY = "AIzaSy..."
OPENAI_API_KEY = "sk-..."
ENABLE_TTS = "true"
TTS_ENGINE = "gtts"
```

**For Google Cloud TTS (optional - better voice quality)**:

If you want realistic voices with male/female differentiation, add:

```toml
TTS_ENGINE = "google_cloud"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "abc123..."
private_key = "-----BEGIN PRIVATE KEY-----\nYour key here...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40project.iam.gserviceaccount.com"
```

**How to get Google Cloud TTS credentials**: See `GOOGLE_CLOUD_TTS_SETUP.md`

#### 2.4 Deploy!

1. Click **"Deploy!"** button
2. Wait 2-5 minutes for initial deployment
3. Your app will build and start automatically
4. You'll see logs streaming as it deploys

#### 2.5 Access Your App

Once deployed, your app will be live at:
```
https://YOUR_APP_NAME.streamlit.app
```

Bookmark this URL or share it with others!

---

### Phase 3: Test Your Deployment (15 minutes)

#### 3.1 Basic Functionality Test

1. Open your app URL
2. Verify the interface loads correctly:
   - Sidebar with all configuration options ✓
   - Main area shows welcome message ✓
   - Start/Pause/Stop/Save/Export buttons visible ✓

#### 3.2 Test Simulation

1. Select configurations:
   - **Oncologist**: Conservative
   - **Patient**: Do More
   - **AI Models**: Select Gemini for both (most reliable on free tier)
   - **Case**: Select any pre-defined case
2. Click **"Start Simulation"**
3. Verify:
   - Conversation starts within 10 seconds ✓
   - Messages appear with 2-second delays ✓
   - Oncologist and patient alternate ✓

#### 3.3 Test Pause Functionality

1. During simulation, click **"Pause"**
2. Verify: Conversation stops immediately ✓
3. Click **"Resume"**
4. Verify: Conversation continues ✓

#### 3.4 Test Text-to-Speech (if enabled)

1. Enable **"Voice"** in sidebar
2. Start a new simulation
3. Verify: Audio plays automatically for each message ✓
4. Test pause: Audio stops when paused ✓

#### 3.5 Test Save & Export

1. After simulation completes or stop it
2. Click **"Save"**
3. Verify: Success message appears ✓
4. Click **"Export"** → **"Export as Text"**
5. Verify: Export succeeds ✓

**Note**: Saved conversations and exports are stored temporarily. They'll be deleted when the app restarts (free tier limitation).

---

## 🔧 Updating Your Deployment

### Update Code

Whenever you push new code to GitHub:

```bash
git add .
git commit -m "Your commit message"
git push
```

Streamlit Cloud will **automatically detect the changes** and redeploy your app (takes 1-2 minutes).

### Update Secrets

If you need to update API keys or other secrets:

1. Go to https://share.streamlit.io/
2. Click on your app
3. Click the hamburger menu (**⋮**) → **"Settings"**
4. Navigate to **"Secrets"** tab
5. Edit your secrets
6. Click **"Save"**
7. App will automatically restart with new secrets

---

## 🐛 Troubleshooting

### App Won't Start

**Symptom**: Deployment fails or app shows error on startup

**Solutions**:
1. Check app logs in Streamlit Cloud dashboard
2. Verify all secrets are configured correctly (no typos)
3. Ensure at least one valid API key is provided
4. Check requirements.txt matches your local environment

### "No API key found" Error

**Symptom**: App loads but shows error when starting simulation

**Solution**:
1. Go to app settings → Secrets
2. Verify secret names match exactly:
   - `ANTHROPIC_API_KEY` (not `ANTHROPIC_KEY`)
   - `GOOGLE_API_KEY` (not `GEMINI_API_KEY`)
   - `OPENAI_API_KEY` (not `OPENAI_KEY`)
3. Ensure values are wrapped in quotes: `GOOGLE_API_KEY = "your_key"`
4. Save and wait for app to restart

### TTS Not Working

**Symptom**: No audio plays even with voice enabled

**Solutions**:

For gTTS:
- Should work immediately, no configuration needed
- If not working, check browser console for errors
- Try a different browser (Chrome works best)

For Google Cloud TTS:
- Verify `[gcp_service_account]` section is in secrets
- Check all fields from credentials JSON are included
- Verify `private_key` includes `\n` for newlines
- **Recommendation**: Start with gTTS, add Google Cloud later

### "Memory limit exceeded" Error

**Symptom**: App crashes with memory error

**Cause**: Streamlit Cloud free tier has 1GB RAM limit

**Solutions**:
1. Use `requirements-gemini-only.txt` instead of full `requirements.txt`:
   ```bash
   # Rename files locally
   mv requirements.txt requirements-all.txt
   mv requirements-gemini-only.txt requirements.txt
   git commit -am "Reduce dependencies"
   git push
   ```
2. Disable providers you're not using
3. Upgrade to Streamlit Cloud paid tier ($20/month for 4GB RAM)

### App Sleeps After Inactivity

**Symptom**: App takes 30-60 seconds to load on first access

**Cause**: Free tier apps sleep after 7 days of inactivity

**Solution**: This is normal behavior. No action needed. App wakes up automatically when accessed.

### Conversation Not Saving

**Symptom**: Saved conversations disappear after app restart

**Cause**: Free tier has ephemeral storage

**Solutions**:
1. **Accept it**: This is expected behavior for free tier
2. **Use export instead**: Export conversations as PDF/JSON before app restarts
3. **Add persistent storage**: Integrate external database (Supabase, PlanetScale) - requires code changes
4. **Upgrade**: Use paid Streamlit Cloud tier with persistent storage

### Slow Response Times

**Symptom**: Simulation is slow or unresponsive

**Causes**:
1. API rate limits (your LLM provider)
2. Cold start after inactivity
3. Network latency

**Solutions**:
1. Wait for app to fully wake up (first load after sleep)
2. Check API key quotas/limits with your provider
3. Try different LLM model (e.g., Gemini is faster than Claude Opus)

---

## 🔐 Security Best Practices

### ✅ DO:

- Use Streamlit Cloud's secrets management
- Commit `.env.example` (template only, no real keys)
- Keep `.streamlit/secrets.toml` in `.gitignore`
- Use separate API keys for dev/production
- Regularly rotate API keys
- Monitor API usage in provider dashboards

### ❌ DON'T:

- Commit `.env` file to GitHub
- Commit `.streamlit/secrets.toml` to GitHub
- Commit Google Cloud credentials JSON files
- Share your app URL publicly if using expensive APIs (risk of abuse)
- Hardcode API keys in source code
- Use production API keys for testing

---

## 💰 Cost Estimates

### Streamlit Community Cloud
- **Deployment**: FREE
- **Hosting**: FREE (with limitations)
- **Bandwidth**: FREE (generous limits)

### LLM API Costs (Pay-as-you-go)

**Google Gemini** (Recommended for free tier):
- Gemini 1.5 Flash: FREE up to 1M tokens/day
- Gemini 1.5 Pro: FREE up to 50 requests/day
- **Your use case**: Likely stays within free tier

**Anthropic Claude**:
- Claude Sonnet: ~$3 per 1M input tokens
- Claude Haiku: ~$0.25 per 1M input tokens
- **Your use case**: ~$0.01-0.05 per conversation

**OpenAI**:
- GPT-4 Turbo: ~$10 per 1M input tokens
- GPT-3.5 Turbo: ~$0.50 per 1M input tokens
- **Your use case**: ~$0.02-0.10 per conversation

**Google Cloud TTS**:
- FREE: First 1M characters/month
- After: ~$16 per 1M characters
- **Your use case**: ~500 conversations fit in free tier

**Estimated Monthly Cost for Moderate Use**:
- Using Gemini only: $0/month
- Using Claude Haiku: $5-10/month
- Using GPT-4: $20-50/month

---

## 📊 Monitoring Your Deployment

### View App Logs

1. Go to https://share.streamlit.io/
2. Click your app
3. Logs appear at bottom of page
4. Use for debugging errors

### Monitor API Usage

Check usage in each provider's dashboard:
- **Anthropic**: https://console.anthropic.com/
- **Google Gemini**: https://makersuite.google.com/
- **OpenAI**: https://platform.openai.com/usage
- **Google Cloud**: https://console.cloud.google.com/billing

### Check App Health

- **Response time**: Should respond within 1-2 seconds (after wake-up)
- **Error rate**: Should be <1% under normal use
- **Memory usage**: View in Streamlit Cloud dashboard

---

## 🔄 Alternative Deployment Options

If Streamlit Community Cloud doesn't meet your needs:

### Hugging Face Spaces
- **Cost**: Free tier available
- **Pros**: Good for ML/AI apps
- **Cons**: More complex than Streamlit Cloud
- **When**: Need GPU or more compute

### Railway.app
- **Cost**: ~$5/month (no free tier)
- **Pros**: More resources, persistent storage
- **When**: Need production features

### Google Cloud Run
- **Cost**: Pay-per-use (~$0.10/month for low traffic)
- **Pros**: Scalable, professional-grade
- **Cons**: Requires Docker knowledge
- **When**: High traffic or enterprise use

### Heroku
- **Cost**: ~$7/month (no free tier since 2022)
- **Pros**: Easy deployment
- **When**: Budget allows, want simplicity

---

## 🎓 Learning Resources

### Streamlit Cloud Documentation
- Official Docs: https://docs.streamlit.io/streamlit-community-cloud
- Deploy Tutorial: https://docs.streamlit.io/streamlit-community-cloud/get-started
- Secrets Management: https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management

### LLM API Documentation
- Anthropic Claude: https://docs.anthropic.com/
- Google Gemini: https://ai.google.dev/docs
- OpenAI: https://platform.openai.com/docs

### Git & GitHub
- GitHub Docs: https://docs.github.com/
- Git Tutorial: https://www.atlassian.com/git/tutorials

---

## 🆘 Getting Help

### Streamlit Community
- Forum: https://discuss.streamlit.io/
- Discord: https://discord.gg/streamlit

### GitHub Issues
- Report bugs or request features in your repository's Issues tab

### API Provider Support
- Check each provider's documentation and support channels

---

## ✅ Deployment Checklist

Use this checklist to ensure everything is ready:

### Before Deployment
- [ ] Code committed to git
- [ ] `.gitignore` includes `.streamlit/secrets.toml`
- [ ] `.env` and credentials files not committed
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] At least one valid API key obtained

### During Deployment
- [ ] Streamlit Cloud account created
- [ ] App deployed from GitHub
- [ ] Secrets configured correctly
- [ ] App starts without errors

### After Deployment
- [ ] App URL accessible
- [ ] Simulation runs successfully
- [ ] Pause/Resume works
- [ ] TTS works (if enabled)
- [ ] Save/Export work
- [ ] API costs monitored

---

## 🎉 Success!

Your Medical Visit Simulator is now deployed and accessible to the world!

**Share your app**: `https://your-app-name.streamlit.app`

**Next steps**:
1. Share with colleagues and students
2. Gather feedback
3. Iterate and improve
4. Monitor usage and costs

---

**Questions?** Check `README.md` for application details or `GOOGLE_CLOUD_TTS_SETUP.md` for TTS setup.

**Happy simulating!** 🏥🤖
