"""Base class for LLM clients."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def converse(
            self,
            messages: List[Dict[str, Any]],
            tools: Optional[List[Dict[str, Any]]] = None,
            system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a conversation to the LLM."""
        pass

    @abstractmethod
    def extract_text_content(self, response: Dict[str, Any]) -> str:
        """Extract text content from response."""
        pass

    @abstractmethod
    def has_tool_use(self, response: Dict[str, Any]) -> bool:
        """Check if response contains tool use request."""
        pass

    @abstractmethod
    def get_tool_use(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract tool use request from response."""
        pass