"""
Base Agent Class
Defines the interface and common functionality for all conversation agents
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, List, Dict
from llm_providers.base_provider import BaseLLMProvider


class BaseAgent(ABC):
    """Base class for conversation agents (oncologists and patients)"""

    def __init__(
        self,
        name: str,
        role: str,
        llm_provider: BaseLLMProvider,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Initialize agent

        Args:
            name: Agent's display name (e.g., "Dr. Smith")
            role: Agent's role (e.g., "oncologist", "patient")
            llm_provider: LLM provider instance to use for generation
            temperature: Sampling temperature for responses
            max_tokens: Maximum tokens per response
        """
        self.name = name
        self.role = role
        self.llm_provider = llm_provider
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt that defines this agent's personality and behavior

        Returns:
            System prompt string
        """
        pass

    async def speak(
        self,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = True
    ) -> AsyncIterator[str]:
        """
        Generate agent's response

        Args:
            context: Current context or message to respond to
            conversation_history: Previous conversation messages
            stream: Whether to stream the response

        Yields:
            Response text chunks
        """
        system_prompt = self.get_system_prompt()

        async for chunk in self.llm_provider.generate(
            system_prompt=system_prompt,
            user_message=context,
            conversation_history=conversation_history,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=stream
        ):
            yield chunk

    def get_display_name(self) -> str:
        """Get display name for UI"""
        return self.name

    def get_role(self) -> str:
        """Get agent role"""
        return self.role

    def get_model_info(self) -> str:
        """Get information about the LLM model being used"""
        return self.llm_provider.get_model_name()
