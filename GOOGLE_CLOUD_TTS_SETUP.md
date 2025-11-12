# Google Cloud Text-to-Speech Setup Guide

This guide will help you set up Google Cloud TTS for the Medical Visit Simulator. The setup takes about 5 minutes and gives you **1 million free characters per month** - plenty for most use cases.

## Why Google Cloud TTS?

- **Realistic neural voices** - Much better quality than gTTS
- **Voice differentiation** - Male voice for doctor, female voice for patient
- **Free tier** - 1 million characters/month (a typical conversation uses ~2,000 characters)
- **Fast** - Audio generation is quick and responsive

## Setup Steps

### 1. Create Google Cloud Account (Free)

1. Go to https://console.cloud.google.com/
2. Sign in with your Google account
3. Accept the terms of service if prompted
4. No credit card required for free tier!

### 2. Create a New Project

1. In the Google Cloud Console, click the project dropdown at the top
2. Click "New Project"
3. Enter a project name (e.g., "medical-visit-simulator")
4. Click "Create"
5. Wait for the project to be created (takes ~30 seconds)

### 3. Enable Text-to-Speech API

1. Go to https://console.cloud.google.com/apis/library/texttospeech.googleapis.com
2. Make sure your project is selected in the dropdown at the top
3. Click **"Enable"**
4. Wait for the API to be enabled

### 4. Create Service Account

1. Go to **IAM & Admin** > **Service Accounts**
   - Direct link: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click **"Create Service Account"**
3. Enter details:
   - **Service account name**: `medical-visit-tts` (or any name)
   - **Description**: "Text-to-Speech for Medical Visit Simulator"
4. Click **"Create and Continue"**
5. Grant role:
   - Select **"Cloud Text-to-Speech User"** role
   - Click **"Continue"**
6. Click **"Done"** (skip the optional steps)

### 5. Create and Download Key

1. Find your service account in the list
2. Click the **three dots** (⋮) on the right
3. Select **"Manage keys"**
4. Click **"Add Key"** > **"Create new key"**
5. Select **JSON** format
6. Click **"Create"**
7. A JSON file will download automatically - **save this file somewhere safe!**
   - Example location: `~/Downloads/medical-visit-simulator-credentials.json`

### 6. Configure Your Application

1. Open your `.env` file in the medical_visit_simulator directory
2. Add the path to your JSON credentials file:

```
GOOGLE_APPLICATION_CREDENTIALS=/Users/yourname/Downloads/medical-visit-simulator-credentials.json
```

**Important**: Use the **absolute path** to the file (full path from root)

3. Make sure these lines are also in your `.env`:

```
ENABLE_TTS=true
TTS_ENGINE=google_cloud
```

### 7. Test It!

1. Run the application: `streamlit run app.py`
2. Enable "Voice" in the sidebar
3. Select "Google Cloud (Recommended, Free Tier)" as the TTS engine
4. Start a simulation
5. You should hear realistic voices! 🎉

## Troubleshooting

### "Could not automatically determine credentials"

**Problem**: The credentials file path is incorrect

**Solution**:
- Make sure the path in `.env` is absolute (starts with `/` on Mac/Linux or `C:\` on Windows)
- Check that the file exists at that location
- Try wrapping the path in quotes if it contains spaces

### "Permission denied" or "Access denied"

**Problem**: The service account doesn't have the right permissions

**Solution**:
1. Go back to IAM & Admin > Service Accounts
2. Click on your service account
3. Go to "Permissions" tab
4. Make sure "Cloud Text-to-Speech User" role is assigned

### "Text-to-Speech API has not been used"

**Problem**: The API isn't enabled for your project

**Solution**:
1. Go to https://console.cloud.google.com/apis/library/texttospeech.googleapis.com
2. Make sure your project is selected
3. Click "Enable"

## Free Tier Limits

- **Neural2 voices** (highest quality): 1 million characters/month free
- After free tier: $0.000016 per character (~$16 per million characters)
- A typical 10-minute conversation uses ~2,000 characters
- So you can do **~500 conversations per month for free**

## Security Note

**Keep your JSON credentials file private!**
- Don't commit it to git (it's in `.gitignore`)
- Don't share it with others
- If compromised, you can revoke it in the Google Cloud Console and create a new one

## Still Need Help?

If you're stuck, you can:
1. Use the simpler gTTS option (set `TTS_ENGINE=gtts` in `.env`)
2. Check the official docs: https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries
3. Review the error messages in the Streamlit interface

---

**Total setup time**: ~5 minutes
**Cost**: Free (up to 1M characters/month)
**Result**: Realistic conversational voices! 🎤
