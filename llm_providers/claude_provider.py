"""
Anthropic Claude LLM Provider
"""
import anthropic
from typing import AsyncIterator, Optional, List, Dict
from .base_provider import BaseLLMProvider


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude API provider"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = anthropic.Anthropic(api_key=api_key)

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
        Generate response using Claude API

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
            messages = []

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
                with self.client.messages.stream(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=messages
                ) as stream:
                    for text in stream.text_stream:
                        yield text
            else:
                # Non-streaming response
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=messages
                )
                yield response.content[0].text

        except Exception as e:
            error_msg = self._build_error_message(e)
            yield f"[Error: {error_msg}]"

    def get_model_name(self) -> str:
        """Get model name"""
        return f"Claude ({self.model})"

    def validate_api_key(self) -> bool:
        """Validate API key is set"""
        return bool(self.api_key and len(self.api_key) > 0)
