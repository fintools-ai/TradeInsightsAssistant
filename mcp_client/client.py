"""MCP client for communicating with the OpenInterest server."""

import subprocess
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
import sys

from agent.constants import MCP_COMMAND, MCP_ARGS

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for MCP OpenInterest server."""

    def __init__(self):
        """Initialize the MCP client."""
        self.process = None
        self.request_id = 0
        self.is_initialized = False
        self.command = MCP_COMMAND
        self.args = MCP_ARGS

    async def start(self):
        """Start the MCP server process."""
        try:
            logger.info("Starting MCP server...")
            logger.info(f"Command: {self.command} {' '.join(self.args)}")

            # Start the process
            self.process = await asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Check if process started successfully
            await asyncio.sleep(0.5)

            if self.process.returncode is not None:
                # Process already exited, capture error
                stderr_data = await self.process.stderr.read()
                stderr_text = stderr_data.decode()
                logger.error(f"MCP server failed to start. Exit code: {self.process.returncode}")
                logger.error(f"Error output: {stderr_text}")
                raise RuntimeError(f"MCP server exited with code {self.process.returncode}: {stderr_text}")

            # Start error reader task
            asyncio.create_task(self._read_stderr())

            # Give server time to fully start
            await asyncio.sleep(1)

            # Initialize connection
            await self._initialize()

            logger.info("MCP server started successfully")

        except Exception as e:
            logger.error(f"Failed to start MCP server: {str(e)}")
            # Try to get more info
            if self.process:
                try:
                    stderr_data = await self.process.stderr.read()
                    if stderr_data:
                        logger.error(f"Server stderr: {stderr_data.decode()}")
                except:
                    pass
            raise

    async def _read_stderr(self):
        """Continuously read stderr for debugging."""
        if not self.process:
            return

        try:
            while True:
                line = await self.process.stderr.readline()
                if not line:
                    break
                logger.debug(f"MCP stderr: {line.decode().strip()}")
        except:
            pass

    async def stop(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            logger.info("MCP server stopped")

    async def _initialize(self):
        """Initialize the MCP connection."""
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "0.1.0",
                "capabilities": {},  # Required by fastmcp schema
                "clientInfo": {      # Required by fastmcp schema
                    "name": "TradeInsightsAgent",
                    "version": "0.1.0"
                }
            },
            "id": self._get_request_id()
        }

        try:
            response = await self._send_request(request)
            logger.info(f"MCP initialized: {response}")
            
            # Send initialized notification as required by MCP protocol
            initialized_request = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            # Send notification (no response expected)
            request_str = json.dumps(initialized_request) + "\n"
            self.process.stdin.write(request_str.encode())
            await self.process.stdin.drain()
            
            # Wait a bit for server to complete initialization
            await asyncio.sleep(0.5)
            
            self.is_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize MCP connection: {str(e)}")
            raise

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server."""
        if not self.is_initialized:
            raise RuntimeError("MCP client not initialized")
            
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": self._get_request_id()
        }

        response = await self._send_request(request)
        return response.get("result", {}).get("tools", [])

    async def call_tool(
            self,
            tool_name: str,
            arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool response
        """
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": self._get_request_id()
        }

        response = await self._send_request(request)

        # Extract result
        if "result" in response:
            content = response["result"].get("content", [])
            if content and "text" in content[0]:
                return json.loads(content[0]["text"])

        return response

    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server and get response."""
        if not self.process:
            raise RuntimeError("MCP server not started")

        # Check if process is still running
        if self.process.returncode is not None:
            raise RuntimeError(f"MCP server exited with code {self.process.returncode}")

        try:
            # Send request
            request_str = json.dumps(request) + "\n"
            logger.debug(f"Sending request: {request_str.strip()}")
            self.process.stdin.write(request_str.encode())
            await self.process.stdin.drain()

            # Read response with timeout
            response_line = await asyncio.wait_for(
                self.process.stdout.readline(),
                timeout=30.0
            )
            response_str = response_line.decode().strip()

            if not response_str:
                # Check if process died
                if self.process.returncode is not None:
                    stderr_data = await self.process.stderr.read()
                    raise RuntimeError(f"MCP server crashed: {stderr_data.decode()}")
                raise RuntimeError("Empty response from MCP server")

            logger.debug(f"Received response: {response_str[:100]}...")
            return json.loads(response_str)

        except asyncio.TimeoutError:
            raise RuntimeError("Timeout waiting for MCP server response")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {response_str}")
            raise RuntimeError(f"Invalid JSON from MCP server: {e}")

    def _get_request_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id