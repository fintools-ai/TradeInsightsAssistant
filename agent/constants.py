"""Constants for Trading Insights Agent."""

import os

# Agent Info
AGENT_NAME = "Trading Insights Agent"
AGENT_VERSION = "1.0.0"

# AWS Bedrock Configuration
BEDROCK_REGION = "us-east-1"
BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"
BEDROCK_MAX_TOKENS = 4096
BEDROCK_TEMPERATURE = 0.1

# MCP Server Configuration
MCP_COMMAND = "mcp-openinterest-server"
MCP_ARGS = []

# Storage Configuration
STORAGE_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "output")
SAVE_ANALYSIS = True

# Import prompts from private repo
try:
    from llm_agent_prompts.open_interest import SYSTEM_PROMPT, ANALYSIS_PROMPT_TEMPLATE
except ImportError:
    # Fallback prompts if private repo is not available
    SYSTEM_PROMPT = """You are a quantitative options analyst specializing in institutional open interest analysis."""
    ANALYSIS_PROMPT_TEMPLATE = """Please provide a comprehensive analysis of the open interest data."""