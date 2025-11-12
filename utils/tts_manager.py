"""
Text-to-Speech Manager
Handles TTS generation with multiple engine support
"""
import os
import asyncio
import tempfile
from typing import Optional, Literal
from io import BytesIO
import streamlit as st


class TTSManager:
    """Manages text-to-speech generation and playback"""

    def __init__(
        self,
        engine: Literal["google_cloud", "gtts"] = "gtts",
        enable_tts: bool = True
    ):
        """
        Initialize TTS Manager

        Args:
            engine: TTS engine to use ("google_cloud" or "gtts")
            enable_tts: Whether TTS is enabled
        """
        self.engine = engine
        self.enable_tts = enable_tts
        self.google_cloud_client = None

        if engine == "google_cloud" and enable_tts:
            try:
                from google.cloud import texttospeech
                from google.oauth2 import service_account

                # Try to use Streamlit secrets first (for deployment)
                if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
                    credentials = service_account.Credentials.from_service_account_info(
                        st.secrets["gcp_service_account"]
                    )
                    self.google_cloud_client = texttospeech.TextToSpeechClient(credentials=credentials)
                else:
                    # Fall back to environment variable (for local development with credentials file)
                    self.google_cloud_client = texttospeech.TextToSpeechClient()
            except Exception as e:
                st.warning(f"Google Cloud TTS not available: {e}. Falling back to gTTS.")
                self.engine = "gtts"

    def synthesize(
        self,
        text: str,
        speaker_role: Literal["oncologist", "patient"],
        voice_config: Optional[dict] = None
    ) -> Optional[bytes]:
        """
        Synthesize text to speech audio

        Args:
            text: Text to synthesize
            speaker_role: Role of speaker (determines voice)
            voice_config: Optional voice configuration override

        Returns:
            Audio bytes (MP3 format) or None if TTS disabled
        """
        if not self.enable_tts or not text.strip():
            return None

        try:
            if self.engine == "google_cloud" and self.google_cloud_client:
                return self._synthesize_google_cloud(text, speaker_role, voice_config)
            else:
                return self._synthesize_gtts(text, speaker_role)
        except Exception as e:
            st.error(f"TTS generation failed: {e}")
            return None

    def _synthesize_google_cloud(
        self,
        text: str,
        speaker_role: str,
        voice_config: Optional[dict] = None
    ) -> bytes:
        """Synthesize using Google Cloud TTS"""
        from google.cloud import texttospeech

        # Default voice configuration
        if not voice_config:
            # Male voice for doctor, female for patient
            if speaker_role == "oncologist":
                voice_name = "en-US-Neural2-D"  # Male voice
                gender = texttospeech.SsmlVoiceGender.MALE
            else:  # patient
                voice_name = "en-US-Neural2-C"  # Female voice
                gender = texttospeech.SsmlVoiceGender.FEMALE
        else:
            voice_name = voice_config.get("name", "en-US-Neural2-C")
            gender_str = voice_config.get("gender", "FEMALE")
            gender = getattr(texttospeech.SsmlVoiceGender, gender_str)

        # Create synthesis input
        input_text = texttospeech.SynthesisInput(text=text)

        # Configure voice
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice_name,
            ssml_gender=gender
        )

        # Configure audio output
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.5,  # 1.5x speed (faster)
            pitch=0.0  # Normal pitch
        )

        # Generate audio
        response = self.google_cloud_client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config
        )

        return response.audio_content

    def _synthesize_gtts(
        self,
        text: str,
        speaker_role: str
    ) -> bytes:
        """
        Synthesize using gTTS (free, basic quality)

        Note: gTTS uses the same voice for all speakers.
        For voice differentiation, use Google Cloud TTS (free tier available).
        """
        from gtts import gTTS

        # Generate speech with gTTS
        tts = gTTS(text=text, lang='en', slow=False)

        # Save to BytesIO
        audio_bytes_io = BytesIO()
        tts.write_to_fp(audio_bytes_io)
        audio_bytes_io.seek(0)

        return audio_bytes_io.read()

    def estimate_duration(self, audio_bytes: bytes) -> float:
        """
        Estimate audio duration based on file size

        Args:
            audio_bytes: Audio file bytes

        Returns:
            Estimated duration in seconds
        """
        # MP3 bitrate estimation: assuming ~32 kbps average for speech
        # 32 kbps = 4000 bytes per second
        # Add 0.5s buffer
        estimated_seconds = len(audio_bytes) / 4000.0 + 0.5
        return max(estimated_seconds, 1.0)  # Minimum 1 second

    async def play_audio(
        self,
        audio_bytes: bytes,
        wait: bool = True,
        container: Optional[st.delta_generator.DeltaGenerator] = None
    ):
        """
        Play audio in Streamlit

        Args:
            audio_bytes: Audio bytes to play
            wait: Whether to wait for audio to finish
            container: Streamlit container to display audio in
        """
        if not audio_bytes:
            return

        # Display audio player
        if container:
            container.audio(audio_bytes, format="audio/mp3", autoplay=True)
        else:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

        # Wait for audio to finish if requested
        if wait:
            duration = self.estimate_duration(audio_bytes)
            await asyncio.sleep(duration + 0.5)  # Add 0.5s buffer

    async def speak(
        self,
        text: str,
        speaker_role: Literal["oncologist", "patient"],
        wait: bool = True,
        container: Optional[st.delta_generator.DeltaGenerator] = None
    ):
        """
        Synthesize and play text

        Args:
            text: Text to speak
            speaker_role: Role of speaker
            wait: Whether to wait for audio to finish
            container: Streamlit container for audio player
        """
        if not self.enable_tts:
            return

        # Synthesize audio
        audio_bytes = self.synthesize(text, speaker_role)

        if audio_bytes:
            # Play audio
            await self.play_audio(audio_bytes, wait=wait, container=container)
