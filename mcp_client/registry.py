"""MCP Registry for loading servers from JSON configuration."""

import json
import logging
from typing import Dict, List, Any
from pathlib import Path

from .client import MCPClient

logger = logging.getLogger(__name__)

class MCPRegistry:
    """Registry for managing MCP servers from JSON config."""
    
    def __init__(self, config_path: str = "mcp_servers.json"):
        self.config_path = config_path
        self.servers: Dict[str, MCPClient] = {}
        self.tools_map: Dict[str, str] = {}  # tool_name -> server_name
        
    def load_config(self) -> List[Dict[str, Any]]:
        """Load server configurations from JSON file."""
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        return config.get("servers", [])
    
    async def start_all(self):
        """Start all servers from config."""
        configs = self.load_config()
        
        for config in configs:
            await self.start_server(config)
    
    async def start_server(self, config: Dict[str, Any]):
        """Start a single server from config."""
        name = config["name"]
        command = config["command"]
        args = config.get("args", [])
        
        try:
            logger.info(f"Starting MCP server: {name}")
            
            client = MCPClient()
            # Set command and args
            client.command = command
            client.args = args
            
            await client.start()
            
            # Get and register tools
            tools = await client.list_tools()
            for tool in tools:
                self.tools_map[tool['name']] = name
                
            self.servers[name] = client
            logger.info(f"Started server {name} with {len(tools)} tools")
            
        except Exception as e:
            logger.error(f"Failed to start server {name}: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool call to appropriate server."""
        server_name = self.tools_map.get(tool_name)
        if not server_name or server_name not in self.servers:
            raise RuntimeError(f"Tool {tool_name} not found")
            
        return await self.servers[server_name].call_tool(tool_name, arguments)
    
    async def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all tools from all servers."""
        all_tools = []
        for server_name, client in self.servers.items():
            tools = await client.list_tools()
            all_tools.extend(tools)
        return all_tools
    
    async def stop_all(self):
        """Stop all servers."""
        for client in self.servers.values():
            await client.stop()
        self.servers.clear()
        self.tools_map.clear()