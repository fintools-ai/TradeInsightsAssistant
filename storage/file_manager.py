"""File manager for saving analysis outputs."""

import os
import json
from datetime import datetime
from typing import Dict, Any

from agent.constants import STORAGE_OUTPUT_DIR, SAVE_ANALYSIS


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
            metadata: Dict[str, Any]
    ) -> str:
        """
        Save analysis to filesystem.

        Args:
            ticker: Stock ticker
            analysis_text: Analysis content
            metadata: Additional metadata

        Returns:
            Path to saved file
        """
        if not SAVE_ANALYSIS:
            return ""

        # Create directory structure
        date_str = datetime.now().strftime("%Y%m%d")
        time_str = datetime.now().strftime("%H%M%S")

        ticker_dir = os.path.join(self.output_dir, ticker, date_str)
        os.makedirs(ticker_dir, exist_ok=True)

        # Save analysis
        filename = f"{ticker}_{time_str}_analysis.md"
        filepath = os.path.join(ticker_dir, filename)

        with open(filepath, 'w') as f:
            # Add metadata header
            f.write(f"# {ticker} Analysis\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Query: {metadata.get('query', 'N/A')}\n")
            f.write(f"Days Analyzed: {metadata.get('days', 'N/A')}\n\n")
            f.write("---\n\n")

            # Add analysis
            f.write(analysis_text)

        # Save metadata
        meta_filename = f"{ticker}_{time_str}_metadata.json"
        meta_filepath = os.path.join(ticker_dir, meta_filename)

        with open(meta_filepath, 'w') as f:
            json.dump(metadata, f, indent=2)

        return filepath