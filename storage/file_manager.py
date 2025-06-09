"""File manager for saving analysis outputs."""

import os
import json
from datetime import datetime
from typing import Dict, Any

from agent.constants import STORAGE_OUTPUT_DIR

class FileManager:
    """Manages saving analysis outputs to filesystem."""

    def __init__(self):
        """Initialize the file manager."""
        self.output_dir = STORAGE_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def save_analysis(
            self,
            ticker: str,
            analysis_text: str,
            metadata: Dict[str, Any],
            force_save: bool = False
    ) -> str:
        """
        Save analysis to filesystem if saving is enabled or explicitly requested.

        Args:
            ticker: Stock ticker
            analysis_text: Analysis content
            metadata: Additional metadata
            force_save: Whether to save regardless of SAVE_ANALYSIS flag

        Returns:
            Path to saved file or empty string if not saved
        """
        save_enabled = os.environ.get("SAVE_ANALYSIS", "false").lower() == "true"
        if not save_enabled and not force_save:
            return ""

        date_str = datetime.now().strftime("%Y%m%d")
        time_str = datetime.now().strftime("%H%M%S")
        ticker_dir = os.path.join(self.output_dir, ticker.upper(), date_str)
        os.makedirs(ticker_dir, exist_ok=True)

        filename = f"{ticker}_{time_str}_analysis.md"
        filepath = os.path.join(ticker_dir, filename)

        with open(filepath, 'w') as f:
            f.write(f"# {ticker} Analysis\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Query: {metadata.get('query', 'N/A')}\n")
            f.write(f"Days Analyzed: {metadata.get('days', 'N/A')}\n\n")
            f.write("---\n\n")
            f.write(analysis_text)

        meta_filepath = os.path.join(ticker_dir, f"{ticker}_{time_str}_metadata.json")
        with open(meta_filepath, 'w') as meta_file:
            json.dump(metadata, meta_file, indent=2)

        print(f"📁 Analysis saved to: {filepath}")
        return filepath

    def save_manual_response(self, text: str, query: str) -> str:
        """
        Save the last assistant message manually with default ticker.

        Args:
            text: The assistant message
            query: The query it was responding to

        Returns:
            Path to saved file
        """
        return self.save_analysis(
            ticker="MANUAL",
            analysis_text=text,
            metadata={"query": query, "manual_save": True, "timestamp": datetime.now().isoformat()},
            force_save=True
        )
