# Entry point and orchestrator logic combined for update

import asyncio
import logging
import sys
import os
from datetime import datetime

from agent.orchestrator import TradingInsightsOrchestrator
from llm_service.bedrock_service.client import BedrockClient
from llm_service.claude_service.claude_client import ClaudeAPIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def show_banner():
    print("""
╔════════════════════════════════════════════════════════════════╗
║        🔍 TradeInsightsAssistant — Options Intelligence CLI     ║
║                                                                ║
║    AI-powered analysis of options open interest & positioning  ║
║    Type natural queries. Discover trade setups. Learn fast.    ║
╚════════════════════════════════════════════════════════════════╝
""")

def select_llm_service():
    print("\n" + "="*60)
    print("Select LLM Service:")
    print("="*60)
    print("1. AWS Bedrock (Claude via AWS)")
    print("2. Claude API (Direct Anthropic)")
    print("="*60)

    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice == "1":
            print("\n✓ Using AWS Bedrock")
            return BedrockClient()
        elif choice == "2":
            if not os.environ.get("ANTHROPIC_API_KEY"):
                print("\n⚠️  ANTHROPIC_API_KEY environment variable not set!")
                print("Please set it using: export ANTHROPIC_API_KEY='your-key-here'")
                continue
            print("\n✓ Using Claude API (Direct)")
            return ClaudeAPIClient()
        else:
            print("Invalid choice. Please enter 1 or 2.")

async def main():
    show_banner()
    llm_client = select_llm_service()
    orchestrator = TradingInsightsOrchestrator(llm_client)

    try:
        print("\nStarting Trading Insights Agent...")
        await orchestrator.start()

        print("="*60)
        print("💬 Example queries:")
        print("="*60)
        print("  - 'Analyze SPY open interest for next 5 days'")
        print("  - 'What's the options flow telling us about AAPL?'")
        print("  - 'Show me support and resistance levels for TSLA'")
        print("  - 'What are the key option levels for QQQ?'")
        print("="*60)
        print("Type your question or command. Type 'exit' to quit.")
        while True:
            user_input = input("\n📊 You: ").strip()

            if user_input.lower() in ('exit', 'quit'):
                print("\nShutting down...")
                break
            elif user_input.lower() == 'clear':
                orchestrator.clear_history()
                print("✓ Conversation history cleared.")
                continue
            elif not user_input:
                continue

            print("\n🤖 Agent: Analyzing...\n")
            start = datetime.now()
            response = await orchestrator.process_message(user_input)
            print(response)
            print("\n⏱️  Time taken: {:.1f} sec".format((datetime.now() - start).total_seconds()))

            if os.environ.get("SAVE_ANALYSIS", "false").lower() != "true":
                save_choice = input("\n💾 Do you want to save this response? (y/n): ").strip().lower()
                if save_choice == 'y':
                    await orchestrator.save_last_response(user_input, force=True)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        await orchestrator.stop()
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
