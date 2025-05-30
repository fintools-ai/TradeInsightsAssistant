"""Main entry point for Trading Insights Agent."""

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


def select_llm_service():
    """Let user select which LLM service to use."""
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
            # Check if API key is set
            if not os.environ.get("ANTHROPIC_API_KEY"):
                print("\n⚠️  ANTHROPIC_API_KEY environment variable not set!")
                print("Please set it using: export ANTHROPIC_API_KEY='your-key-here'")
                continue
            print("\n✓ Using Claude API (Direct)")
            return ClaudeAPIClient()
        else:
            print("Invalid choice. Please enter 1 or 2.")


async def main():
    """Main function to run the chat interface."""
    # Let user select LLM service
    llm_client = select_llm_service()

    # Create orchestrator with selected client
    orchestrator = TradingInsightsOrchestrator(llm_client)

    try:
        # Start services
        print("\nStarting Trading Insights Agent...")
        await orchestrator.start()

        print("\n" + "="*60)
        print("🚀 Trading Insights Agent - Options Analysis Chat")
        print("="*60)
        print("\nCommands:")
        print("  - Type your question about options/stocks")
        print("  - Type 'clear' to clear conversation history")
        print("  - Type 'exit' or 'quit' to exit")
        print("\nExample queries:")
        print("  - 'Analyze SPY open interest for next 5 days'")
        print("  - 'What's the options flow telling us about AAPL?'")
        print("  - 'Show me support and resistance levels for TSLA'")
        print("  - 'What are the key option levels for QQQ?'")
        print("="*60 + "\n")

        while True:
            try:
                # Get user input
                user_input = input("\n📊 You: ").strip()

                # Check for commands
                if user_input.lower() in ['exit', 'quit']:
                    print("\nShutting down...")
                    break
                elif user_input.lower() == 'clear':
                    orchestrator.clear_history()
                    print("✓ Conversation history cleared.")
                    continue
                elif not user_input:
                    continue

                # Process message
                print("\n🤖 Agent: Analyzing...\n")

                start_time = datetime.now()
                response = await orchestrator.process_message(user_input)
                end_time = datetime.now()

                print(response)
                print(f"\n⏱️  Analysis completed in {(end_time - start_time).total_seconds():.1f} seconds")

            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in chat loop: {str(e)}")
                print(f"\n❌ Error: {str(e)}")

    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        print(f"\n❌ Failed to start: {str(e)}")
    finally:
        # Clean up
        await orchestrator.stop()
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)