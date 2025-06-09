import asyncio
import logging
import sys
import os
from datetime import datetime

from agent.orchestrator import TradingInsightsOrchestrator
from llm_service.bedrock_service.client import BedrockClient
from llm_service.claude_service.claude_client import ClaudeAPIClient

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

console = Console()

def show_banner():
    console.print(Panel.fit("""
🔍 TradeInsightsAssistant — Options Intelligence CLI

AI-powered analysis of options open interest & positioning
Type natural queries. Discover trade setups. Learn fast.
""", title="Welcome", border_style="blue"))

def select_llm_service():
    console.print("\n[bold cyan]Select LLM Service:[/bold cyan]")
    console.print("1. AWS Bedrock (Claude via AWS)")
    console.print("2. Claude API (Direct Anthropic)")

    while True:
        choice = Prompt.ask("Enter your choice", choices=["1", "2"])
        if choice == "1":
            console.print("\n✅ Using AWS Bedrock")
            return BedrockClient()
        elif choice == "2":
            if not os.environ.get("ANTHROPIC_API_KEY"):
                console.print("\n[red]⚠️  ANTHROPIC_API_KEY environment variable not set![/red]")
                console.print("Please set it using: [bold]export ANTHROPIC_API_KEY='your-key-here'[/bold]")
                continue
            console.print("\n✅ Using Claude API (Direct)")
            return ClaudeAPIClient()

async def main():
    show_banner()
    llm_client = select_llm_service()
    orchestrator = TradingInsightsOrchestrator(llm_client)

    try:
        console.print("\n[bold]Starting Trading Insights Agent...[/bold]")
        console.print("\n[bold yellow]💬 Example queries:[/bold yellow]")
        console.print("- 'Analyze SPY open interest for next 5 days'")
        console.print("- 'What's the options flow telling us about AAPL?'")
        console.print("- 'Show me support and resistance levels for TSLA'")
        console.print("- 'What are the key option levels for QQQ?'")
        console.print("\nType your question or use '/exit' to quit.\n")

        await orchestrator.start()

        while True:
            user_input = Prompt.ask("📊 You").strip()

            if user_input.lower() in ('/exit', '/quit'):
                console.print("\nShutting down...")
                break
            elif user_input.lower() == '/clear':
                orchestrator.clear_history()
                console.print("[green]✓ Conversation history cleared.[/green]")
                continue
            elif not user_input:
                continue

            with Progress(SpinnerColumn(), TimeElapsedColumn(), transient=True) as progress:
                progress.add_task("Analyzing...", total=None)
                start = datetime.now()
                response = await orchestrator.process_message(user_input)

            console.print("\n[bold magenta]🤖 Agent:[/bold magenta]\n")
            console.print(Markdown(response))
            console.print("\n⏱️  Time taken: {:.1f} sec".format((datetime.now() - start).total_seconds()))

            if os.environ.get("SAVE_ANALYSIS", "false").lower() != "true":
                save_choice = Prompt.ask("💾 Do you want to save this response?", choices=["y", "n"])
                if save_choice == 'y':
                    await orchestrator.save_last_response(user_input, force=True)

    except KeyboardInterrupt:
        console.print("\n[red]Interrupted by user.[/red]")
    finally:
        await orchestrator.stop()
        console.print("\n👋 Goodbye!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[red]Interrupted. Exiting gracefully...[/red]")
        sys.exit(0)
