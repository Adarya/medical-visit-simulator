"""
Configuration settings for the Medical Visit Simulator
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings"""

    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_CLOUD_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

    # Simulation defaults
    DEFAULT_MAX_TURNS = 20
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 1000

    # Available models
    CLAUDE_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]

    GEMINI_MODELS = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash"
    ]

    OPENAI_MODELS = [
        "gpt-4-turbo-preview",
        "gpt-4",
        "gpt-3.5-turbo"
    ]

    # Database settings
    DATABASE_PATH = "data/conversations.db"

    # Export settings
    EXPORT_DIR = "exports"

    # Conversation ending signals
    ENDING_SIGNALS = [
        "follow up",
        "see you in",
        "any other questions",
        "schedule",
        "next appointment",
        "we'll meet again",
        "touch base",
        "check back"
    ]

    # Text-to-Speech settings
    ENABLE_TTS = os.getenv("ENABLE_TTS", "true").lower() == "true"
    TTS_ENGINE = os.getenv("TTS_ENGINE", "gtts")  # Default to gtts since it works without setup

    # Voice configurations
    TTS_VOICES = {
        "google_cloud": {
            "oncologist": "en-US-Neural2-D",  # Male voice for doctor
            "patient": "en-US-Neural2-C"  # Female voice for patient
        }
    }

    @classmethod
    def get_api_key(cls, provider: str) -> str:
        """Get API key for specified provider"""
        key_map = {
            "claude": cls.ANTHROPIC_API_KEY,
            "anthropic": cls.ANTHROPIC_API_KEY,
            "gemini": cls.GOOGLE_API_KEY,
            "google": cls.GOOGLE_API_KEY,
            "openai": cls.OPENAI_API_KEY
        }
        return key_map.get(provider.lower(), "")

    @classmethod
    def get_models_for_provider(cls, provider: str) -> list:
        """Get available models for specified provider"""
        model_map = {
            "claude": cls.CLAUDE_MODELS,
            "anthropic": cls.CLAUDE_MODELS,
            "gemini": cls.GEMINI_MODELS,
            "google": cls.GEMINI_MODELS,
            "openai": cls.OPENAI_MODELS
        }
        return model_map.get(provider.lower(), [])


# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs(Settings.EXPORT_DIR, exist_ok=True)
