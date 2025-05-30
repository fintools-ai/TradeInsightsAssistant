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

            # Start the process with increased buffer limit to handle large responses
            self.process = await asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=100 * 1024 * 1024  # 100MB limit instead of default 64KB
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
                decoded_line = line.decode().strip()
                # Always log MCP server output at INFO level for visibility
                logger.info(f"[MCP Server] {decoded_line}")
        except Exception as e:
            logger.error(f"Error reading MCP stderr: {str(e)}")

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

        logger.info(f"[MCP] Calling tool '{tool_name}' with arguments: {json.dumps(arguments, indent=2)}")
        
        # Use longer timeout for tool calls, especially for analyze_open_interest
        timeout = 300.0  # 5 minutes for tool calls
        if tool_name == "analyze_open_interest":
            # Even longer timeout for OI analysis with multiple days
            days = arguments.get("days", 1)
            timeout = 120.0 + (days * 60.0)  # Base 2 minutes + 1 minute per day
            logger.info(f"[MCP] Using extended timeout of {timeout}s for {days} days of OI data")
        
        response = await self._send_request(request, timeout=timeout)

        # Extract result
        logger.info(f"[MCP] Raw response type: {type(response)}")
        logger.info(f"[MCP] Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
        
        if "result" in response:
            result = response["result"]
            logger.info(f"[MCP] Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
            
            content = result.get("content", [])
            logger.info(f"[MCP] Content type: {type(content)}, length: {len(content) if isinstance(content, list) else 'N/A'}")
            
            if content and isinstance(content, list) and len(content) > 0:
                first_content = content[0]
                logger.info(f"[MCP] First content item keys: {list(first_content.keys()) if isinstance(first_content, dict) else 'N/A'}")
                
                if "text" in first_content:
                    text_data = first_content["text"]
                    logger.info(f"[MCP] Text data length: {len(text_data)}")
                    
                    try:
                        tool_result = json.loads(text_data)
                        logger.info(f"[MCP] Tool '{tool_name}' returned successfully")
                        
                        # Print the full tool response for debugging
                        logger.debug("[MCP] Full tool response:")
                        logger.info("=" * 80)
                        logger.info(json.dumps(tool_result, indent=2))
                        logger.info("=" * 80)
                        
                        return tool_result
                    except json.JSONDecodeError as e:
                        logger.error(f"[MCP] Failed to parse tool result JSON: {e}")
                        logger.error(f"[MCP] Raw text data: {text_data[:500]}...")
                        raise
                else:
                    logger.error(f"[MCP] No 'text' field in content[0]: {first_content}")
            else:
                logger.error(f"[MCP] Empty or invalid content: {content}")
        else:
            logger.error(f"[MCP] No 'result' field in response")
        
        logger.warning(f"[MCP] Tool '{tool_name}' returned unexpected format: {response}")
        return response

    async def _send_request(self, request: Dict[str, Any], timeout: float = 60.0) -> Dict[str, Any]:
        """Send a request to the MCP server and get response."""
        if not self.process:
            raise RuntimeError("MCP server not started")

        # Check if process is still running
        if self.process.returncode is not None:
            raise RuntimeError(f"MCP server exited with code {self.process.returncode}")

        try:
            # Send request
            request_str = json.dumps(request) + "\n"
            logger.info(f"[MCP] Sending request: {request['method']} (id: {request.get('id', 'N/A')})")
            logger.debug(f"[MCP] Full request: {request_str.strip()}")
            
            self.process.stdin.write(request_str.encode())
            await self.process.stdin.drain()

            # Read response with custom reader that handles large responses
            logger.info(f"[MCP] Waiting for response with timeout={timeout}s...")
            start_time = asyncio.get_event_loop().time()
            
            response_str = await self._read_json_response(timeout=timeout)
            
            elapsed_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"[MCP] Response received in {elapsed_time:.2f} seconds")

            if not response_str:
                # Check if process died
                if self.process.returncode is not None:
                    stderr_data = await self.process.stderr.read()
                    raise RuntimeError(f"MCP server crashed: {stderr_data.decode()}")
                raise RuntimeError("Empty response from MCP server")

            logger.debug(f"[MCP] Response preview: {response_str[:200]}...")
            
            response_json = json.loads(response_str)
            
            # Log response size
            response_size = len(response_str)
            if response_size > 1024 * 1024:  # > 1MB
                logger.info(f"[MCP] Large response: {response_size / (1024 * 1024):.2f} MB")
            else:
                logger.info(f"[MCP] Response size: {response_size} bytes")
            
            # Check for errors in response
            if "error" in response_json:
                logger.error(f"[MCP] Error in response: {response_json['error']}")
            
            return response_json

        except asyncio.TimeoutError:
            elapsed = asyncio.get_event_loop().time() - start_time
            raise RuntimeError(f"Timeout waiting for MCP server response after {elapsed:.1f}s (timeout={timeout}s)")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {response_str}")
            raise RuntimeError(f"Invalid JSON from MCP server: {e}")

    async def _read_json_response(self, timeout: float = 30.0) -> str:
        """Read a complete JSON response from stdout, handling large responses."""
        try:
            # MCP protocol sends responses as single lines of JSON
            # We already increased the buffer limit to 100MB when creating the subprocess
            response_line = await asyncio.wait_for(
                self.process.stdout.readline(),
                timeout=timeout
            )
            
            if not response_line:
                logger.warning("[MCP] Received empty response line")
                return ""
            
            response_str = response_line.decode().strip()
            
            # Log first 500 chars of response for debugging
            if len(response_str) > 500:
                logger.debug(f"[MCP] Response preview: {response_str[:500]}...")
            else:
                logger.debug(f"[MCP] Response: {response_str}")
            
            return response_str
            
        except asyncio.TimeoutError:
            logger.error(f"[MCP] Timeout after {timeout}s waiting for response")
            # Try to read any partial data that might be available
            try:
                partial = await asyncio.wait_for(self.process.stdout.read(1024), timeout=1.0)
                if partial:
                    logger.error(f"[MCP] Partial data available: {partial.decode()[:100]}...")
            except:
                pass
            raise
        except Exception as e:
            logger.error(f"[MCP] Error reading JSON response: {str(e)}")
            raise

    def _get_request_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id
