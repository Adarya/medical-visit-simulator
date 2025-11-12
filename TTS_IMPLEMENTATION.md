# Text-to-Speech Implementation

## Summary
TTS has been carefully re-added to the Medical Visit Simulator without breaking the pause functionality.

## How It Works

### 1. **TTS Manager Initialization**
- Created when conversation starts in `initialize_conversation()`
- Supports both gTTS (default, works immediately) and Google Cloud TTS (better quality)
- Settings from sidebar: Enable/Disable and Engine selection

### 2. **Audio Generation**
When a new message is received in `run_simulation_step()`:
```python
# Generate TTS if enabled
if config.get("enable_tts", False):
    audio_bytes = tts_manager.synthesize(message.content, message.role)
    st.session_state.pending_audio = audio_bytes
```

### 3. **Audio Playback**
Audio plays on the next render cycle:
```python
# Play pending audio if available
if st.session_state.pending_audio:
    st.audio(st.session_state.pending_audio, format="audio/mp3", autoplay=True)
    st.session_state.pending_audio = None  # Clear after playing
```

### 4. **Pause Compatibility**
- Audio generation happens only when not paused
- Pending audio is cleared when Stop is pressed
- Pause button still works instantly

## Features

### gTTS (Default)
- Works immediately, no setup required
- Basic quality, same voice for all speakers
- Free and unlimited

### Google Cloud TTS (Recommended)
- Realistic neural voices
- Different voices: Male (doctor), Female (patient)
- 1.5x speed for faster playback
- Free tier: 1 million characters/month
- Requires 5-minute setup (see GOOGLE_CLOUD_TTS_SETUP.md)

## Testing TTS

1. **Test with gTTS (immediate)**:
   - Run the app
   - Enable "Voice" in sidebar
   - Select "gTTS (Basic, Works Immediately)"
   - Start simulation
   - Audio should play for each message

2. **Test with Google Cloud TTS**:
   - Set up credentials (see GOOGLE_CLOUD_TTS_SETUP.md)
   - Select "Google Cloud (Recommended, Free Tier)"
   - Start simulation
   - Should hear different voices for doctor/patient

3. **Test Pause with TTS**:
   - Start simulation with TTS enabled
   - Click Pause during playback
   - Audio stops, conversation pauses
   - Click Resume - continues from where it left off

## Implementation Details

### Files Modified:

1. **app.py:320-389** - `run_simulation_step()`
   - Added audio generation after message received
   - Stores in `pending_audio` session state

2. **app.py:564-566** - Main display
   - Plays pending audio before next simulation step
   - Clears pending audio after playing

3. **app.py:418-431, 452-461** - Start/Stop buttons
   - Clears pending audio on Start/Stop

### Key Design Decisions:

1. **Deferred Playback**: Audio is generated when message arrives but played on next render. This prevents audio from interrupting the UI update.

2. **Session State Storage**: Using `st.session_state.pending_audio` ensures audio plays exactly once.

3. **Cleanup on Stop**: Clearing pending audio prevents old audio from playing when restarting.

4. **Error Handling**: TTS failures show warning but don't stop simulation.

## Troubleshooting

### No Audio Playing
- Check "Enable Voice" is checked in sidebar
- Check volume is not muted
- Try gTTS first (simpler, no setup)

### Google Cloud TTS Not Working
- Check credentials are set in .env
- Verify Text-to-Speech API is enabled in Google Cloud Console
- Check the info message in sidebar for setup instructions

### Audio Cuts Off on Pause
- This is expected behavior
- Audio stops immediately when paused
- New audio plays when resumed

## Future Improvements
- Volume control slider
- Speed control (currently fixed at 1.5x for Google Cloud)
- More voice options
- Save audio with conversation export