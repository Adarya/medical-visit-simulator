"""
Google Gemini LLM Provider
"""
import google.generativeai as genai
from typing import AsyncIterator, Optional, List, Dict
from .base_provider import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider"""

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro", **kwargs):
        super().__init__(api_key, model, **kwargs)
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = True
    ) -> AsyncIterator[str]:
        """
        Generate response using Gemini API

        Args:
            system_prompt: System prompt defining agent behavior
            user_message: Current message to respond to
            conversation_history: Previous conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response

        Yields:
            Response text chunks
        """
        try:
            # Gemini uses different message format - combine system prompt with first user message
            # and build history
            history = []

            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg["role"] == "user" else "model"
                    history.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })

            # Create chat session
            chat = self.client.start_chat(history=history)

            # Always include the system prompt to reinforce persona on every turn
            full_message = f"{system_prompt}\n\n{user_message}"

            # Generation config
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )

            if stream:
                # Streaming response
                response = chat.send_message(
                    full_message,
                    generation_config=generation_config,
                    stream=True
                )
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            else:
                # Non-streaming response
                response = chat.send_message(
                    full_message,
                    generation_config=generation_config,
                    stream=False
                )
                yield response.text

        except Exception as e:
            error_msg = self._build_error_message(e)
            yield f"[Error: {error_msg}]"

    def get_model_name(self) -> str:
        """Get model name"""
        return f"Gemini ({self.model})"

    def validate_api_key(self) -> bool:
        """Validate API key is set"""
        return bool(self.api_key and len(self.api_key) > 0)
