"""Main orchestrator for the Trading Insights Agent."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from bedrock_service.client import BedrockClient
from mcp_client.registry import MCPRegistry
from storage.file_manager import FileManager
from agent.constants import ANALYSIS_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class TradingInsightsOrchestrator:
    def __init__(self):
        self.bedrock = BedrockClient()
        self.mcp_registry = MCPRegistry()
        self.storage = FileManager()
        self.conversation_history = []
        self.mcp_tools = []

    async def start(self):
        """Start the orchestrator services."""
        await self.mcp_registry.start_all()
        self.mcp_tools = await self.mcp_registry.get_all_tools()
        logger.info(f"MCP servers started with {len(self.mcp_tools)} tools")


    async def stop(self):
        """Stop the orchestrator services."""
        await self.mcp_registry.stop_all()
        logger.info("Trading Insights Agent stopped")

    async def process_message(self, user_message: str) -> str:
        """
        Process a user message and return the analysis.

        Args:
            user_message: User's question or request

        Returns:
            Analysis response
        """
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": [{"text": user_message}]
            })

            # Get tool definitions for Bedrock
            tool_definitions = self._get_tool_definitions()

            # First, send to Claude to understand the request
            initial_response = await self.bedrock.converse(
                messages=self.conversation_history,
                tools=tool_definitions
            )

            # Check if Claude wants to use a tool
            if self.bedrock.has_tool_use(initial_response):
                tool_use = self.bedrock.get_tool_use(initial_response)

                if tool_use:
                    # Extract tool name and arguments
                    tool_name = tool_use.get("name")
                    tool_args = tool_use.get("input", {})

                    # Call MCP tool
                    logger.info(f"Calling tool '{tool_name}' with args: {tool_args}")
                    tool_result = await self.mcp_registry.call_tool(tool_name, tool_args)

                    # Add Claude's response to history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": [
                            {"text": self.bedrock.extract_text_content(initial_response)},
                            {"toolUse": tool_use}
                        ]
                    })

                    # Add tool result to history
                    self.conversation_history.append({
                        "role": "user",
                        "content": [{
                            "toolResult": {
                                "toolUseId": tool_use.get("toolUseId"),
                                "content": [{"text": json.dumps(tool_result)}]
                            }
                        }]
                    })

                    # Create analysis prompt
                    analysis_prompt = self._create_analysis_prompt(tool_result)

                    # Send back to Claude for detailed analysis
                    final_response = await self.bedrock.converse(
                        messages=self.conversation_history + [{
                            "role": "user",
                            "content": [{"text": analysis_prompt}]
                        }]
                    )

                    # Extract analysis
                    analysis_text = self.bedrock.extract_text_content(final_response)

                    # Save analysis if it's OI analysis
                    if tool_name == "analyze_open_interest":
                        ticker = tool_args.get("ticker", "UNKNOWN")
                        filepath = self.storage.save_analysis(
                            ticker=ticker,
                            analysis_text=analysis_text,
                            metadata={
                                "query": user_message,
                                "tool_args": tool_args,
                                "timestamp": datetime.now().isoformat()
                            }
                        )

                        if filepath:
                            analysis_text += f"\n\n---\n*Analysis saved to: {filepath}*"

                    # Add to history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": [{"text": analysis_text}]
                    })

                    return analysis_text

            # If no tool use, just return Claude's response
            response_text = self.bedrock.extract_text_content(initial_response)
            self.conversation_history.append({
                "role": "assistant",
                "content": [{"text": response_text}]
            })

            return response_text

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"Error processing your request: {str(e)}"

    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to Bedrock tool definitions."""
        bedrock_tools = []

        for tool in self.mcp_tools:
            # Ensure description is not empty (Bedrock requirement)
            description = tool.get("description", "").strip()
            if not description:
                if tool["name"] == "analyze_open_interest":
                    description = "Analyzes options open interest data for a given ticker over specified days"
                else:
                    description = f"Tool: {tool['name']}"
            
            bedrock_tool = {
                "toolSpec": {
                    "name": tool["name"],
                    "description": description,
                    "inputSchema": {
                        "json": tool.get("inputSchema", {})
                    }
                }
            }
            bedrock_tools.append(bedrock_tool)

        return bedrock_tools

    def _create_analysis_prompt(self, tool_result: Dict[str, Any]) -> str:
        """Create the detailed analysis prompt."""
        ticker = tool_result.get("ticker", "")

        prompt = f"""
Based on the open interest data provided for {ticker}, please provide a comprehensive analysis following this exact structure:

{ANALYSIS_PROMPT_TEMPLATE}

The raw open interest data has been provided in the tool response. Analyze all strikes, identify patterns, and provide specific actionable trading recommendations.

Remember to:
- Be extremely precise with price levels (to the nearest $0.25)
- Provide exact strike prices and expiration dates for all trade recommendations
- Include specific entry/exit criteria
- Format everything in clear markdown with proper sections
"""

        return prompt

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")