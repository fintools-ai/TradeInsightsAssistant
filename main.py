"""Main entry point for Trading Insights Agent."""

import asyncio
import logging
import sys
from datetime import datetime

from agent.orchestrator import TradingInsightsOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to run the chat interface."""
    # Create orchestrator
    orchestrator = TradingInsightsOrchestrator()

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