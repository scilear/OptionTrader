#!/usr/bin/env python3
"""
scaffold_vault.py

Creates the complete Options-Curriculum Obsidian vault structure with stub notes.

Usage:
    python scaffold_vault.py /path/to/Options-Curriculum
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# Curriculum structure: folder → list of note filenames
CURRICULUM_NOTES: Dict[str, List[str]] = {
    "00-Index": [
        "Home.md",
        "WikiLink-Map.md",
        "Canon-Examples.md",
        "Obsidian-Setup.md",
        "Broker-Comparison.md",
        "Tax-Treatment.md",
        "Common-Mistakes.md",
        "Progress-Dashboard.md",
        "Glossary.md",
    ],
    "01-Foundations": [
        "Options-Basics.md",
        "Greeks-Overview.md",
        "Delta.md",
        "Gamma.md",
        "Theta-Decay.md",
        "Vega.md",
        "IV-vs-HV.md",
        "IV-Rank.md",
        "IV-Percentile.md",
    ],
    "02-Finding-Opportunities": [
        "Ticker-Selection-System.md",
        "Ticker-Criteria-Technical.md",
        "Ticker-Criteria-Fundamental.md",
        "Earnings-Calendar-System.md",
        "Screener-Setup.md",
        "High-Probability-Setup-Checklist.md",
        "Setup-Recognition-Patterns.md",
    ],
    "03-Entry-Exit": [
        "Best-Days-of-Week.md",
        "Intraday-Timing-Open.md",
        "Intraday-Timing-Midday.md",
        "Intraday-Timing-Power-Hour.md",
        "Entry-Confirmation-Signals.md",
        "When-Not-To-Trade.md",
        "Building-Discipline.md",
    ],
    "04-Strategies/Set-and-Forget": [
        "Covered-Call.md",
        "CSP-Cash-Secured-Put.md",
        "Wheel-Strategy.md",
        "Zero-Risk-Collar.md",
    ],
    "04-Strategies/Income": [
        "Iron-Condor.md",
        "Iron-Butterfly.md",
        "Short-Strangle.md",
        "Short-Straddle.md",
        "Vertical-Spread.md",
        "Jade-Lizard.md",
        "Ratio-Spread.md",
    ],
    "04-Strategies/Long-Term": [
        "LEAPS.md",
        "PMCC.md",
        "Diagonal-Spread.md",
        "Calendar-Spread.md",
        "Synthetic-Long.md",
    ],
    "04-Strategies/0DTE": [
        "0DTE-Overview.md",
        "0DTE-Credit-Spread.md",
        "0DTE-Iron-Condor.md",
        "0DTE-Scalping.md",
        "0DTE-Risk-Rules.md",
        "0DTE-Morning-Routine.md",
        "0DTE-Adjustment-Playbook.md",
    ],
    "05-Market-Conditions": [
        "High-IV-Playbook.md",
        "Low-IV-Playbook.md",
        "Trending-Market-Playbook.md",
        "Rangebound-Market-Playbook.md",
        "Earnings-Season-Playbook.md",
    ],
    "06-Risk-Management": [
        "Position-Sizing.md",
        "Max-Loss-Rules.md",
        "Portfolio-Heat.md",
        "Stop-Loss-Strategies.md",
        "Losing-Trade-Mindset.md",
    ],
    "07-Profit-Taking": [
        "Profit-Taking-Rules.md",
        "Rolling-Basics.md",
        "When-To-Take-Profits.md",
    ],
    "08-Adjustments": [
        "Adjustment-Decision-Tree.md",
        "Rolling-for-Credit.md",
        "Inverted-Strangle.md",
        "Converting-to-Fly.md",
        "Repair-Strategies.md",
    ],
    "09-Earnings": [
        "Earnings-Overview.md",
        "IV-Crush-Mechanics.md",
        "Expected-Move-Formula.md",
        "Earnings-Straddle.md",
        "Earnings-IC-Playbook.md",
        "Earnings-Calendar-Play.md",
        "Earnings-Risk-Rules.md",
        "Post-Earnings-Adjustment.md",
    ],
}

# Directories without notes
EMPTY_DIRECTORIES: List[str] = [
    "Charts/outputs",
    "Templates",
    "prompts",
]


def filename_to_title(filename: str) -> str:
    """Convert filename to title case.

    Args:
        filename: Filename with hyphens (e.g., 'Options-Basics.md')

    Returns:
        Title-cased string (e.g., 'Options Basics')
    """
    # Remove .md extension
    name = filename.replace(".md", "")
    # Replace hyphens with spaces
    title = name.replace("-", " ")
    return title


def folder_to_tag(folder: str) -> str:
    """Extract tag from folder name.

    Args:
        folder: Folder path (e.g., '01-Foundations' or '04-Strategies/Income')

    Returns:
        Lowercase tag (e.g., 'foundations' or 'income')
    """
    # Get the last part of the path (after /)
    part = folder.split("/")[-1]
    # Remove leading digits and hyphen
    tag = part.lstrip("0123456789-").lower()
    return tag


def create_stub_content(title: str, tag: str) -> str:
    """Create YAML frontmatter and stub content for a note.

    Args:
        title: Note title
        tag: Tag inferred from folder

    Returns:
        Markdown content with frontmatter
    """
    return f"""---
title: {title}
tags:
  - {tag}
status: stub
related: []
---

# {title}

<!-- stub -->
"""


def scaffold_vault(vault_root: Path) -> Tuple[int, int, int]:
    """Create the complete vault structure.

    Args:
        vault_root: Path to the vault root directory

    Returns:
        Tuple of (directories_created, files_created, files_skipped)
    """
    vault_root = Path(vault_root)
    vault_root.mkdir(parents=True, exist_ok=True)

    dirs_created = 0
    files_created = 0
    files_skipped = 0

    # Create directories for notes
    for folder in CURRICULUM_NOTES.keys():
        dir_path = vault_root / folder
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            dirs_created += 1

        # Create stub files
        tag = folder_to_tag(folder)
        for filename in CURRICULUM_NOTES[folder]:
            file_path = dir_path / filename
            if file_path.exists():
                files_skipped += 1
            else:
                title = filename_to_title(filename)
                content = create_stub_content(title, tag)
                file_path.write_text(content, encoding="utf-8")
                files_created += 1

    # Create empty directories
    for folder in EMPTY_DIRECTORIES:
        dir_path = vault_root / folder
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            dirs_created += 1

    return dirs_created, files_created, files_skipped


def main():
    parser = argparse.ArgumentParser(
        description="Create the Options-Curriculum Obsidian vault structure."
    )
    parser.add_argument(
        "vault_root",
        type=str,
        help="Path to the vault root directory",
    )
    args = parser.parse_args()

    vault_root = Path(args.vault_root)

    try:
        dirs_created, files_created, files_skipped = scaffold_vault(vault_root)
        print(
            f"Created {dirs_created} directories, {files_created} stub files, "
            f"skipped {files_skipped} existing files."
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
