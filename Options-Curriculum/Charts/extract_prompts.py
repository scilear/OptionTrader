#!/usr/bin/env python3
"""
Extract task prompts from TASKBOARD.md and save to individual text files.

Parses tasks in format:
  #### TASK-NNN · Title
  **Complexity:** N (1=haiku, 2=sonnet, 3=opus)
  **Output:** path/to/output.txt
  **Prompt:**
  > Block-quoted prompt text
  ---

Combines global prefix with task-specific prompt and saves as:
  {output_dir}/TASK-NNN.txt
"""

import argparse
import re
import sys
from pathlib import Path


def extract_global_prefix(content: str) -> str:
    """Extract global prompt prefix from '## Global Prompt Prefix' section."""
    match = re.search(
        r"## Global Prompt Prefix\s*\n(.*?)(?:\n---|\Z)",
        content,
        re.DOTALL,
    )
    if not match:
        return ""

    block = match.group(1).strip()
    lines = block.split("\n")
    # Strip leading '> ' blockquote markers
    cleaned = []
    for line in lines:
        if line.startswith("> "):
            cleaned.append(line[2:])
        elif line == ">":
            cleaned.append("")
        else:
            cleaned.append(line)

    return "\n".join(cleaned).strip()


def extract_tasks(content: str, filter_prefix: str | None = None) -> list[dict]:
    """
    Extract all tasks matching pattern: #### TASK-NNN · Title

    Returns list of dicts with: task_id, title, complexity, output_path, prompt
    """
    tasks = []

    # Split on task headings
    task_pattern = r"#### (TASK-\d+) · (.+?)\n"
    matches = list(re.finditer(task_pattern, content))

    for i, match in enumerate(matches):
        task_id = match.group(1)
        title = match.group(2).strip()

        # Apply filter if provided
        if filter_prefix and not task_id.startswith(filter_prefix):
            continue

        # Extract content from this task to the next task (or end)
        start_pos = match.end()
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)

        task_section = content[start_pos:end_pos]

        # Extract complexity line
        complexity_match = re.search(
            r"\*\*Complexity:\*\*\s*(\d+)", task_section
        )
        if not complexity_match:
            print(f"Warning: {task_id} missing Complexity line, skipping")
            continue

        complexity = int(complexity_match.group(1))

        # Extract output path
        output_match = re.search(
            r"\*\*Output:\*\*\s*(.+?)(?:\n|$)", task_section
        )
        if not output_match:
            output_path = ""
        else:
            output_path = output_match.group(1).strip()

        # Extract prompt block (from **Prompt:** to --- or next heading)
        prompt_match = re.search(
            r"\*\*Prompt:\*\*\s*\n(.*?)(?:\n---|\n#### |\Z)",
            task_section,
            re.DOTALL,
        )
        if not prompt_match:
            print(f"Warning: {task_id} missing Prompt block, skipping")
            continue

        prompt_block = prompt_match.group(1).strip()

        # Strip blockquote markers (> prefix)
        prompt_lines = prompt_block.split("\n")
        cleaned_prompt = []
        for line in prompt_lines:
            if line.startswith("> "):
                cleaned_prompt.append(line[2:])
            elif line == ">":
                cleaned_prompt.append("")
            else:
                cleaned_prompt.append(line)

        prompt_text = "\n".join(cleaned_prompt).strip()

        tasks.append({
            "task_id": task_id,
            "title": title,
            "complexity": complexity,
            "output_path": output_path,
            "prompt": prompt_text,
        })

    return tasks


def complexity_to_model(complexity: int) -> str:
    """Map complexity number to model name."""
    mapping = {1: "haiku", 2: "sonnet", 3: "opus"}
    return mapping.get(complexity, "unknown")


def save_prompt_file(
    output_dir: Path,
    task_id: str,
    title: str,
    complexity: int,
    output_path: str,
    global_prefix: str,
    prompt: str,
) -> None:
    """Save formatted prompt to file."""
    model = complexity_to_model(complexity)

    content = f"""# {task_id}: {title}
# Complexity: {complexity}
# Output: {output_path}
# Model: {model}  (1=haiku, 2=sonnet, 3=opus)

## GLOBAL PREFIX
{global_prefix}

## TASK-SPECIFIC PROMPT
{prompt}
"""

    filepath = output_dir / f"{task_id}.txt"
    filepath.write_text(content)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract task prompts from TASKBOARD.md"
    )
    parser.add_argument(
        "--taskboard",
        default="TASKBOARD.md",
        help="Path to TASKBOARD.md (default: TASKBOARD.md)",
    )
    parser.add_argument(
        "--output-dir",
        default="prompts",
        help="Output directory for prompt files (default: prompts)",
    )
    parser.add_argument(
        "--filter",
        default=None,
        help="Only extract tasks matching prefix (e.g., TASK-08)",
    )

    args = parser.parse_args()

    # Read taskboard
    taskboard_path = Path(args.taskboard)
    if not taskboard_path.exists():
        print(f"Error: {args.taskboard} not found")
        sys.exit(1)

    content = taskboard_path.read_text(encoding="utf-8")

    # Extract global prefix
    global_prefix = extract_global_prefix(content)
    if not global_prefix:
        print("Warning: No global prefix found")

    # Extract tasks
    tasks = extract_tasks(content, filter_prefix=args.filter)

    if not tasks:
        print("No tasks extracted")
        sys.exit(0)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save each task
    for task in tasks:
        save_prompt_file(
            output_dir,
            task["task_id"],
            task["title"],
            task["complexity"],
            task["output_path"],
            global_prefix,
            task["prompt"],
        )

    # Print summary
    print(f"Extracted {len(tasks)} prompts to {output_dir}/")


if __name__ == "__main__":
    main()
