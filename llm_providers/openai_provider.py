"""
OpenAI LLM Provider
"""
from openai import OpenAI
from typing import AsyncIterator, Optional, List, Dict
from .base_provider import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider"""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = OpenAI(api_key=api_key)

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
        Generate response using OpenAI API

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
            # Build messages array
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })

            if stream:
                # Streaming response
                stream_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )

                for chunk in stream_response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                # Non-streaming response
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False
                )
                yield response.choices[0].message.content

        except Exception as e:
            error_msg = self._build_error_message(e)
            yield f"[Error: {error_msg}]"

    def get_model_name(self) -> str:
        """Get model name"""
        return f"OpenAI ({self.model})"

    def validate_api_key(self) -> bool:
        """Validate API key is set"""
        return bool(self.api_key and len(self.api_key) > 0)
