"""Base LLM service interface."""
import logging
from abc import ABC, abstractmethod
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger("ai_core")


class BaseLLMService(ABC):
    """Abstract base for all LLM providers."""

    @abstractmethod
    def _build_llm(self):
        """Return a LangChain chat model instance."""
        pass

    def __init__(self):
        self.llm = self._build_llm()
        logger.info(f"{self.__class__.__name__} initialized")

    def chat(self, message: str, system_prompt: str = None) -> str:
        """Send a message and return the response text."""
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))

        logger.info(f"[REQUEST] {message[:100]}...")
        response = self.llm.invoke(messages)
        logger.info(f"[RESPONSE] {response.content[:200]}...")

        return response.content