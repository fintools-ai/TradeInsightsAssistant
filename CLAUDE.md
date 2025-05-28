# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradeInsightsAssistant is an AI-powered chat interface for analyzing daily options Open Interest (OI) data. It uses AWS Bedrock for language processing and integrates with an MCP (Model Context Protocol) server for options data analysis.

## Architecture

### Core Components
- **Agent Orchestrator** (`agent/orchestrator.py`): Main controller that coordinates between Bedrock AI and MCP data server
- **Bedrock Service** (`bedrock_service/client.py`): AWS Bedrock client using Claude 3.5 Sonnet for analysis
- **MCP Client** (`mcp_client/client.py`): Communicates with external OpenInterest MCP server via JSON-RPC
- **Storage Manager** (`storage/file_manager.py`): Handles saving analysis outputs

### Data Flow
1. User asks question about options/stocks via CLI
2. Orchestrator sends request to Bedrock with available MCP tools
3. Bedrock determines which tool to call and extracts parameters
4. MCP client calls external server to fetch OI data
5. Raw data is sent back to Bedrock for detailed analysis
6. Final analysis is returned to user and optionally saved

## Common Commands

### Running the Application
```bash
python main.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
# External MCP server (private repo)
pip install git+ssh://git@github.com/fintools-ai/mcp-openinterest-server.git
```

### Testing
```bash
pytest
pytest-asyncio  # For async tests
```

## Development Notes

### Configuration Constants
- All configuration is centralized in `agent/constants.py`
- AWS Bedrock model: Claude 3.5 Sonnet (update to Opus 4 when available)
- MCP server command: `mcp-openinterest-server`

### Key File Patterns
- Analysis outputs saved to `storage/output/` directory
- Conversation history maintained in orchestrator for context
- All services are async/await based

### Error Handling
- MCP server startup includes timeout and error checking
- Bedrock calls have retry logic and timeout configuration
- Process stderr is monitored for debugging

### Testing Approach
The codebase uses pytest with async support. Test any new functionality with proper async test patterns.