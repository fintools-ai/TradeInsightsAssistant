"""Bedrock Converse API client."""

import json
import logging
from typing import Dict, List, Any, Optional
import boto3
from botocore.config import Config
from llm_service.base import BaseLLMClient

from agent.constants import (
    BEDROCK_REGION,
    BEDROCK_MODEL_ID,
    BEDROCK_MAX_TOKENS,
    BEDROCK_TEMPERATURE,
    SYSTEM_PROMPT
)

logger = logging.getLogger(__name__)


class BedrockClient(BaseLLMClient):
    """AWS Bedrock client using the Converse API."""

    def __init__(self):
        """Initialize the Bedrock client."""
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=BEDROCK_REGION,
            config=Config(
                connect_timeout=60,
                read_timeout=300,
                retries={"max_attempts": 3}
            )
        )
        self.model_id = BEDROCK_MODEL_ID
        self.max_tokens = BEDROCK_MAX_TOKENS
        self.temperature = BEDROCK_TEMPERATURE

    async def converse(
            self,
            messages: List[Dict[str, Any]],
            tools: Optional[List[Dict[str, Any]]] = None,
            system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a conversation to Bedrock using the Converse API.

        Args:
            messages: List of message dictionaries
            tools: Optional list of tool definitions
            system_prompt: Optional system prompt override

        Returns:
            Response from Bedrock
        """
        try:
            # Build the request
            request = {
                "modelId": self.model_id,
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": self.max_tokens,
                    "temperature": self.temperature
                }
            }

            # Add system prompt
            if system_prompt:
                request["system"] = [{"text": system_prompt}]
            else:
                request["system"] = [{"text": SYSTEM_PROMPT}]

            # Add tools if provided
            if tools:
                request["toolConfig"] = {
                    "tools": tools
                }

            # Log the size of the request
            request_json = json.dumps(request)
            request_size = len(request_json)
            logger.info(f"Bedrock request size: {request_size / 1024:.2f} KB")
            
            # Check if any message is too large
            for i, msg in enumerate(messages):
                msg_json = json.dumps(msg)
                msg_size = len(msg_json)
                if msg_size > 100000:  # 100KB
                    logger.warning(f"Message {i} is large: {msg_size / 1024:.2f} KB")
                    # Log the message role
                    logger.info(f"Message {i} role: {msg.get('role', 'unknown')}")
                    # If it's a tool result, log some info
                    content = msg.get("content", [])
                    if content and isinstance(content, list):
                        for item in content:
                            if "toolResult" in item:
                                logger.info(f"Message {i} contains toolResult")

            # Call Bedrock - make it truly async
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.client.converse(**request)
            )
            
            logger.info("Bedrock response received successfully")

            return response

        except Exception as e:
            logger.error(f"Error calling Bedrock: {str(e)}")
            # Log more details about the error
            if hasattr(e, 'response'):
                logger.error(f"Error response: {getattr(e.response, 'text', 'No text')}")
            raise

    def extract_text_content(self, response: Dict[str, Any]) -> str:
        """Extract text content from Bedrock response."""
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
