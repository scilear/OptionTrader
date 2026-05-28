"""validate_vault.py — Obsidian vault validator for Options-Curriculum.

Checks:
  1. WikiLink resolution  ([[Link]] / [[Link|Alias]] forms)
  2. Frontmatter validation  (title + status fields required)
  3. Chart embed existence  (![[name.png]] / ![[name.html]])

Usage:
    python validate_vault.py <vault_root>
    python validate_vault.py <vault_root> --fix-stubs
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------

_TTY = sys.stdout.isatty()

GREEN = "\033[32m" if _TTY else ""
RED = "\033[31m" if _TTY else ""
RESET = "\033[0m" if _TTY else ""

PASS_TAG = f"{GREEN}✓ PASS{RESET}"
FAIL_TAG = f"{RED}✗ FAIL{RESET}"


# ---------------------------------------------------------------------------
# Folder routing for --fix-stubs
# ---------------------------------------------------------------------------

# Prefix → folder mapping (lowercase prefix → relative folder path in vault).
_STUB_FOLDER_MAP: list[tuple[str, str]] = [
    ("greeks-",    "01-Foundations"),
    ("delta",      "01-Foundations"),
    ("gamma",      "01-Foundations"),
    ("theta",      "01-Foundations"),
    ("vega",       "01-Foundations"),
    ("iv-",        "01-Foundations"),
    ("implied-",   "01-Foundations"),
    ("options-",   "01-Foundations"),
    ("put-call",   "01-Foundations"),
    ("volatility-","01-Foundations"),
    ("skew",       "01-Foundations"),
    ("entry-",     "03-Entry-Exit"),
    ("exit-",      "03-Entry-Exit"),
    ("spread-",    "04-Strategies"),
    ("strangle",   "04-Strategies"),
    ("straddle",   "04-Strategies"),
    ("condor",     "04-Strategies"),
    ("butterfly",  "04-Strategies"),
    ("calendar",   "04-Strategies"),
    ("0dte",       "04-Strategies/0DTE"),
    ("earnings",   "09-Earnings"),
    ("risk-",      "06-Risk-Management"),
    ("profit-",    "07-Profit-Taking"),
    ("adjust-",    "08-Adjustments"),
    ("market-",    "05-Market-Conditions"),
    ("regime",     "05-Market-Conditions"),
    ("opportunity","02-Finding-Opportunities"),
    ("scan-",      "02-Finding-Opportunities"),
]

_DEFAULT_STUB_FOLDER = "00-Index"


def _stub_folder(link_name: str) -> str:
    lower = link_name.lower()
    for prefix, folder in _STUB_FOLDER_MAP:
        if lower.startswith(prefix) or lower == prefix.rstrip("-"):
            return folder
    return _DEFAULT_STUB_FOLDER


# ---------------------------------------------------------------------------
# Vault walker — build file index
# ---------------------------------------------------------------------------

def build_file_index(vault_root: Path) -> dict[str, Path]:
    """Return {lowercase_stem: path} for every .md file in the vault.

    Hidden directories, Charts/outputs/, and Templates/ are excluded.
    Template files contain placeholder [[{{...}}]] syntax that is intentional
    and would produce false-positive validation errors.
    """
    charts_outputs = (vault_root / "Charts" / "outputs").resolve()
    templates_dir = (vault_root / "Templates").resolve()
    index: dict[str, Path] = {}
    for path in vault_root.rglob("*.md"):
        # Skip hidden directories anywhere in the path.
        if any(part.startswith(".") for part in path.parts):
            continue
        # Skip Charts/outputs/.
        try:
            path.resolve().relative_to(charts_outputs)
            continue  # inside Charts/outputs/
        except ValueError:
            pass
        # Skip Templates/ — placeholder [[{{...}}]] links are intentional.
        try:
            path.resolve().relative_to(templates_dir)
            continue
        except ValueError:
            pass
        stem_lower = path.stem.lower()
        index[stem_lower] = path
    return index


# ---------------------------------------------------------------------------
# File reader
# ---------------------------------------------------------------------------

def read_lines(path: Path) -> list[str] | None:
    """Read file lines; return None on binary/encoding error."""
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, UnicodeDecodeError):
        return None


# ---------------------------------------------------------------------------
# Check 1: WikiLink resolution
# ---------------------------------------------------------------------------

# Matches [[Target]] and [[Target|Alias]] but NOT ![[...]] (embed).
_WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]]+)\]\]")

# Detects fenced code block boundaries.
_FENCE_RE = re.compile(r"^```")


def check_wikilinks(
    vault_root: Path,
    file_index: dict[str, Path],
) -> list[str]:
    errors: list[str] = []
    charts_outputs = (vault_root / "Charts" / "outputs").resolve()

    for path in sorted(file_index.values()):
        lines = read_lines(path)
        if lines is None:
            continue
        rel = path.relative_to(vault_root)
        in_fence = False
        for lineno, line in enumerate(lines, start=1):
            if _FENCE_RE.match(line.strip()):
                in_fence = not in_fence
            if in_fence:
                continue
            for m in _WIKILINK_RE.finditer(line):
                raw = m.group(1)
                # Strip pipe alias: [[Link|Alias]] → "Link"
                target = raw.split("|")[0]
                # Strip heading anchor: [[Note#Section]] → "Note"
                target = target.split("#")[0].strip()
                # Strip .md suffix if someone wrote [[Note.md]].
                if target.lower().endswith(".md"):
                    target = target[:-3]
                if not target:
                    continue
                if target.lower() not in file_index:
                    errors.append(f"{rel}:{lineno} → [[{raw}]]")
    return errors


# ---------------------------------------------------------------------------
# Check 2: Frontmatter validation
# ---------------------------------------------------------------------------

def parse_frontmatter(lines: list[str]) -> dict | None:
    """Return parsed frontmatter dict, or None if no valid block."""
    if not lines or lines[0].rstrip() != "---":
        return None
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.rstrip() == "---":
            end = i
            break
    if end is None:
        return None
    block = "\n".join(lines[1:end])
    try:
        data = yaml.safe_load(block)
        return data if isinstance(data, dict) else {}
    except yaml.YAMLError:
        return {}


def check_frontmatter(
    vault_root: Path,
    file_index: dict[str, Path],
) -> list[str]:
    errors: list[str] = []
    required_fields = ("title", "status")
    for path in sorted(file_index.values()):
        lines = read_lines(path)
        if lines is None:
            continue
        rel = path.relative_to(vault_root)
        fm = parse_frontmatter(lines)
        if fm is None:
            errors.append(f"{rel}: missing frontmatter")
            continue
        for field in required_fields:
            if field not in fm or fm[field] is None:
                errors.append(f"{rel}: missing field '{field}'")
    return errors


# ---------------------------------------------------------------------------
# Check 3: Chart embed existence
# ---------------------------------------------------------------------------

_EMBED_RE = re.compile(r"!\[\[([^\]]+\.(?:png|html))\]\]", re.IGNORECASE)


def check_chart_embeds(
    vault_root: Path,
    file_index: dict[str, Path],
) -> list[str]:
    charts_outputs = vault_root / "Charts" / "outputs"
    errors: list[str] = []

    for path in sorted(file_index.values()):
        lines = read_lines(path)
        if lines is None:
            continue
        rel = path.relative_to(vault_root)
        in_fence = False
        for lineno, line in enumerate(lines, start=1):
            if _FENCE_RE.match(line.strip()):
                in_fence = not in_fence
            if in_fence:
                continue
            for m in _EMBED_RE.finditer(line):
                filename = m.group(1)
                target = charts_outputs / filename
                if not target.exists():
                    errors.append(f"{rel}:{lineno} → ![[{filename}]]")
    return errors


# ---------------------------------------------------------------------------
# --fix-stubs
# ---------------------------------------------------------------------------

_STUB_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*$")

_STUB_TEMPLATE = """\
---
title: {title}
status: stub
---

# {title}

> Stub note — fill in content.
"""


def fix_stubs(
    vault_root: Path,
    broken_links: list[str],
    file_index: dict[str, Path],
) -> None:
    """Create minimal stub notes for broken WikiLinks that look like note names."""
    # Extract unique target names from broken-link error lines.
    seen: set[str] = set()
    target_re = re.compile(r"→ \[\[([^\]|#]+)")
    for line in broken_links:
        m = target_re.search(line)
        if not m:
            continue
        raw = m.group(1).strip()
        # Strip alias / anchor already done in check, but repeat for safety.
        target = raw.split("|")[0].split("#")[0].strip()
        if target.lower().endswith(".md"):
            target = target[:-3]
        if not target or not _STUB_NAME_RE.match(target):
            continue
        if target.lower() in file_index:
            continue
        seen.add(target)

    for name in sorted(seen):
        folder = _stub_folder(name)
        dest_dir = vault_root / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{name}.md"
        if dest.exists():
            print(f"  [skip] {dest.relative_to(vault_root)} already exists")
            continue
        dest.write_text(_STUB_TEMPLATE.format(title=name), encoding="utf-8")
        # Update index so subsequent stubs know about it.
        file_index[name.lower()] = dest
        print(f"  [created] {dest.relative_to(vault_root)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate an Options-Curriculum Obsidian vault.",
    )
    parser.add_argument("vault_root", type=Path, help="Path to the vault root directory.")
    parser.add_argument(
        "--fix-stubs",
        action="store_true",
        help="Create minimal stub notes for broken WikiLinks.",
    )
    args = parser.parse_args()

    vault_root: Path = args.vault_root.resolve()
    if not vault_root.is_dir():
        print(f"Error: '{vault_root}' is not a directory.", file=sys.stderr)
        sys.exit(2)

    print(f"Vault: {vault_root}\n")

    # Build shared file index once.
    file_index = build_file_index(vault_root)
    print(f"Indexed {len(file_index)} .md files.\n")

    total_errors = 0

    # ------------------------------------------------------------------
    # Check 1: WikiLinks
    # ------------------------------------------------------------------
    print("=" * 60)
    print("CHECK 1: WikiLink resolution")
    print("=" * 60)
    wikilink_errors = check_wikilinks(vault_root, file_index)
    for err in wikilink_errors:
        print(f"  {err}")
    if wikilink_errors:
        print(f"\n  {FAIL_TAG}  ({len(wikilink_errors)} broken link(s))")
        total_errors += len(wikilink_errors)

        if args.fix_stubs:
            print("\n  --fix-stubs: creating stub notes …")
            fix_stubs(vault_root, wikilink_errors, file_index)
            # Re-run after fixes to show residual errors.
            wikilink_errors_after = check_wikilinks(vault_root, file_index)
            residual = len(wikilink_errors_after)
            if residual:
                print(f"  {residual} broken link(s) remain (non-stub-eligible targets).")
            else:
                print(f"  All broken links resolved via stubs.")
            # Adjust total to reflect post-fix state.
            total_errors = total_errors - len(wikilink_errors) + residual
    else:
        print(f"  {PASS_TAG}")

    # ------------------------------------------------------------------
    # Check 2: Frontmatter
    # ------------------------------------------------------------------
    print()
    print("=" * 60)
    print("CHECK 2: Frontmatter validation")
    print("=" * 60)
    fm_errors = check_frontmatter(vault_root, file_index)
    for err in fm_errors:
        print(f"  {err}")
    if fm_errors:
        print(f"\n  {FAIL_TAG}  ({len(fm_errors)} issue(s))")
        total_errors += len(fm_errors)
    else:
        print(f"  {PASS_TAG}")

    # ------------------------------------------------------------------
    # Check 3: Chart embeds
    # ------------------------------------------------------------------
    print()
    print("=" * 60)
    print("CHECK 3: Chart embed existence")
    print("=" * 60)
    embed_errors = check_chart_embeds(vault_root, file_index)
    for err in embed_errors:
        print(f"  {err}")
    if embed_errors:
        print(f"\n  {FAIL_TAG}  ({len(embed_errors)} missing chart(s))")
        total_errors += len(embed_errors)
    else:
        print(f"  {PASS_TAG}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    print("=" * 60)
    if total_errors:
        print(f"{RED}{total_errors} error(s) found.{RESET}")
        sys.exit(1)
    else:
        print(f"{GREEN}All checks passed.{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
