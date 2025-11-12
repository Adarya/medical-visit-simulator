"""
Base LLM Provider Interface
All LLM providers must implement this interface
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Dict, Any, List


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, api_key: str, model: str, **kwargs):
        """
        Initialize the LLM provider

        Args:
            api_key: API key for the provider
            model: Model name to use
            **kwargs: Additional provider-specific parameters
        """
        self.api_key = api_key
        self.model = model
        self.extra_params = kwargs

    @abstractmethod
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
        Generate a response from the LLM

        Args:
            system_prompt: System prompt defining the agent's role
            user_message: Current user message
            conversation_history: List of previous messages [{"role": "...", "content": "..."}]
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Yields:
            str: Response chunks (if streaming) or complete response
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the model being used"""
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate that the API key is set and potentially valid"""
        pass

    def format_conversation_history(
        self,
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> List[Dict[str, str]]:
        """
        Format conversation history to provider's expected format

        Args:
            conversation_history: List of messages

        Returns:
            Formatted conversation history
        """
        if not conversation_history:
            return []
        return conversation_history

    def _build_error_message(self, error: Exception) -> str:
        """Build a user-friendly error message"""
        return f"Error from {self.get_model_name()}: {str(error)}"
