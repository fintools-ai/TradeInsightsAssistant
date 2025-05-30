"""Claude API client using Anthropic SDK."""

import logging
from typing import Dict, List, Any, Optional
import anthropic

from llm_service.base import BaseLLMClient
from agent.constants import (
    CLAUDE_API_KEY,
    CLAUDE_MODEL_ID,
    CLAUDE_MAX_TOKENS,
    CLAUDE_TEMPERATURE,
    SYSTEM_PROMPT
)

logger = logging.getLogger(__name__)


class ClaudeAPIClient(BaseLLMClient):
    """Direct Claude API client using Anthropic SDK."""

    def __init__(self):
        """Initialize the Claude client."""
        self.client = anthropic.AsyncClient(api_key=CLAUDE_API_KEY)
        self.model_id = CLAUDE_MODEL_ID
        self.max_tokens = CLAUDE_MAX_TOKENS
        self.temperature = CLAUDE_TEMPERATURE

    async def converse(
            self,
            messages: List[Dict[str, Any]],
            tools: Optional[List[Dict[str, Any]]] = None,
            system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a conversation to Claude API."""
        try:
            # Convert messages to Anthropic format
            anthropic_messages = self._convert_messages(messages)

            # Build request parameters
            params = {
                "model": self.model_id,
                "messages": anthropic_messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": system_prompt or SYSTEM_PROMPT
            }

            # Add tools if provided
            if tools:
                params["tools"] = self._convert_tools(tools)

            # Make the API call
            response = await self.client.messages.create(**params)

            # Convert response to common format
            return self._format_response(response)

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise

    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert messages from Bedrock format to Anthropic format."""
        anthropic_messages = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", [])

            # Convert content
            anthropic_content = []
            for item in content:
                if isinstance(item, dict):
                    if "text" in item:
                        anthropic_content.append({
                            "type": "text",
                            "text": item["text"]
                        })
                    elif "toolUse" in item:
                        tool_use = item["toolUse"]
                        anthropic_content.append({
                            "type": "tool_use",
                            "id": tool_use.get("toolUseId"),
                            "name": tool_use.get("name"),
                            "input": tool_use.get("input", {})
                        })
                    elif "toolResult" in item:
                        tool_result = item["toolResult"]
                        anthropic_content.append({
                            "type": "tool_result",
                            "tool_use_id": tool_result.get("toolUseId"),
                            "content": tool_result.get("content", [{}])[0].get("text", "")
                        })

            if anthropic_content:
                anthropic_messages.append({
                    "role": role,
                    "content": anthropic_content
                })

        return anthropic_messages

    def _convert_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert tools from Bedrock format to Anthropic format."""
        anthropic_tools = []

        for tool in tools:
            tool_spec = tool.get("toolSpec", {})
            anthropic_tools.append({
                "name": tool_spec.get("name"),
                "description": tool_spec.get("description"),
                "input_schema": tool_spec.get("inputSchema", {}).get("json", {})
            })

        return anthropic_tools

    def _format_response(self, response) -> Dict[str, Any]:
        """Format Anthropic response to common format."""
        # Convert to Bedrock-like format for compatibility
        content = []

        for block in response.content:
            if block.type == "text":
                content.append({"text": block.text})
            elif block.type == "tool_use":
                content.append({
                    "toolUse": {
                        "toolUseId": block.id,
                        "name": block.name,
                        "input": block.input
                    }
                })

        return {
            "output": {
                "message": {
                    "content": content
                }
            }
        }

    def extract_text_content(self, response: Dict[str, Any]) -> str:
        """Extract text content from response."""
        output = response.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])

        text_parts = []
        for item in content:
            if "text" in item:
                text_parts.append(item["text"])

        return "\n".join(text_parts)

    def has_tool_use(self, response: Dict[str, Any]) -> bool:
        """Check if response contains tool use request."""
        output = response.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])

        for item in content:
            if "toolUse" in item:
                return True

        return False

    def get_tool_use(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract tool use request from response."""
        output = response.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])

        for item in content:
            if "toolUse" in item:
                return item["toolUse"]

        return None