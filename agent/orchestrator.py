import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from llm_service.base import BaseLLMClient
from mcp_client.registry import MCPRegistry
from storage.file_manager import FileManager
from agent.constants import ANALYSIS_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

class TradingInsightsOrchestrator:
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client
        self.mcp_registry = MCPRegistry()
        self.storage = FileManager()
        self.conversation_history = []
        self.mcp_tools = []

    async def start(self):
        await self.mcp_registry.start_all()
        self.mcp_tools = await self.mcp_registry.get_all_tools()
        logger.info(f"MCP servers started with {len(self.mcp_tools)} tools")

    async def stop(self):
        await self.mcp_registry.stop_all()
        logger.info("Trading Insights Agent stopped")

    async def process_message(self, user_message: str) -> str:
        try:
            self.conversation_history.append({
                "role": "user",
                "content": [{"text": user_message}]
            })

            tool_definitions = self._get_tool_definitions()

            initial_response = await self.llm_client.converse(
                messages=self.conversation_history,
                tools=tool_definitions
            )

            if self.llm_client.has_tool_use(initial_response):
                tool_use = self.llm_client.get_tool_use(initial_response)

                if tool_use:
                    tool_name = tool_use.get("name")
                    tool_args = tool_use.get("input", {})

                    logger.info(f"Calling tool '{tool_name}' with args: {tool_args}")
                    tool_result = await self.mcp_registry.call_tool(tool_name, tool_args)

                    self.conversation_history.append({
                        "role": "assistant",
                        "content": [
                            {"text": self.llm_client.extract_text_content(initial_response)},
                            {"toolUse": tool_use}
                        ]
                    })

                    self.conversation_history.append({
                        "role": "user",
                        "content": [{
                            "toolResult": {
                                "toolUseId": tool_use.get("toolUseId"),
                                "content": [{"text": json.dumps(tool_result)}]
                            }
                        }]
                    })

                    analysis_prompt = self._create_analysis_prompt(tool_result)

                    final_response = await self.llm_client.converse(
                        messages=self.conversation_history + [{
                            "role": "user",
                            "content": [{"text": analysis_prompt}]
                        }],
                        tools=tool_definitions
                    )

                    analysis_text = self.llm_client.extract_text_content(final_response)

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

                    self.conversation_history.append({
                        "role": "assistant",
                        "content": [{"text": analysis_text}]
                    })

                    return analysis_text

            response_text = self.llm_client.extract_text_content(initial_response)
            self.conversation_history.append({
                "role": "assistant",
                "content": [{"text": response_text}]
            })

            return response_text

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"Error processing your request: {str(e)}"

    async def save_last_response(self, query: str, force: bool = True):
        """Save the last LLM response manually."""
        for msg in reversed(self.conversation_history):
            if msg["role"] == "assistant" and "text" in msg["content"][0]:
                text = msg["content"][0]["text"]
                self.storage.save_manual_response(text=text, query=query)
                return
        print("❌ No LLM response found to save.")

    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        bedrock_tools = []
        for tool in self.mcp_tools:
            description = tool.get("description", "").strip()
            if not description:
                description = f"Tool: {tool['name']}"
            bedrock_tools.append({
                "toolSpec": {
                    "name": tool["name"],
                    "description": description,
                    "inputSchema": {"json": tool.get("inputSchema", {})}
                }
            })
        return bedrock_tools

    def _create_analysis_prompt(self, tool_result: Dict[str, Any]) -> str:
        ticker = tool_result.get("ticker", "")
        return f"""
Based on the open interest data provided for {ticker}, please provide a comprehensive analysis following this exact structure:

{ANALYSIS_PROMPT_TEMPLATE}

The raw open interest data has been provided in the tool response. Analyze all strikes, identify patterns, and provide specific actionable trading recommendations.

Remember to:
- Be extremely precise with price levels (to the nearest $0.25)
- Provide exact strike prices and expiration dates for all trade recommendations
- Include specific entry/exit criteria
- Format everything in clear markdown with proper sections
"""

    def clear_history(self):
        self.conversation_history = []
        logger.info("Conversation history cleared")
