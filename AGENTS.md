# AGENTS.md — Codebase Protocols, Build/Test Commands, and Style Guide

## 🚦 ABSOLUTE: jCodemunch-MCP Code Exploration Policy
- **Code navigation and search MUST use jCodemunch-MCP tools.** Never use legacy Read, Grep, Glob, or Bash for file, symbol, or text exploration!
- To scan file content: Use `get_file_outline` or `get_file_content` only.
- To search names or comments: Use `search_symbols` or `search_text` only.
- To examine structure of a directory: Use `get_file_tree` or `get_repo_outline` only.
- Always call `resolve_repo` on the working directory first; if it is not indexed, run `index_folder` and wait for completion. Never skip this step.
- If you are unclear about what tool to use, default to the most restrictive and ask the user.
- If ambiguity remains, review this AGENTS.md or .github/copilot-instructions.md.

---

## 📦 Build, Lint, and Test Protocols

### Python Virtual Environment
- All commands require an activated Python venv, usually `.venv` in the repo root.
- On Linux/Unix/macOS:
    ```bash
    source .venv/bin/activate
    ```
- If a `.venv` does not exist, create one:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

### Install Requirements
```
pip install -r requirements.txt
```
- **Main dependencies:** duckdb, ib_insync, pandas, streamlit, yfinance, pytest

### Running the Application
#### Streamlit Dashboard (dev/prod)
```bash
./scripts/run_streamlit.sh dev
# or for production mode
./scripts/run_streamlit.sh prod
```

#### Pipeline/Batch Ingestion
```bash
./scripts/run_pipeline_and_notify.sh
# or:
python scripts/run_pipeline.py
```

### Linting
- **No explicit linter config detected.**
- Follow PEP8 and Black conventions (see below for specifics).
- Use `flake8` (if installed):
    ```bash
    flake8 src/ tests/
    ```

### Unit/Integration Testing
#### Full Test Suite
```bash
pytest
```
#### Run a Single Test File
```bash
pytest tests/test_alerts_logic.py
```
#### Run a Named Test Function (recommended for debugging)
```bash
pytest tests/test_alerts_logic.py -k test_pessimistic_gate_blocks
```
#### Generate Coverage Report
```bash
pytest --cov=src
```

---

## 🖋️ Code Style Guidelines

### Imports
- Standard library imports first, third-party next, then local imports.
- Use absolute imports unless relative is strictly necessary.
- Avoid star imports; be explicit with imported names.
- One import per line preferred.

### Formatting
- **Line length:** 100 characters max.
- **Indentation:** 4 spaces (never tabs).
- Always include a newline at end of file.
- Use Black-compatible formatting: double quotes, trailing commas in multi-line collections.

### Type Hints
- All new functions should use PEP484 type hints for arguments and return types.
- Prefer explicit types, especially for function signatures and public APIs/classes.
- Use `|` (Python 3.10+) for `Union` types, e.g., `str | None`.

### Naming Conventions
- **Modules/filenames:** lowercase_with_underscores.
- **Variables/functions:** lowercase_with_underscores.
- **Classes:** CapitalizedWords (CamelCase).
- **Constants:** ALL_CAPS (only for real constants).
- Be concise but descriptive with function and variable names.

### Error Handling
- Raise precise built-in or custom exceptions with helpful error messages.
- Use `try`/`except` narrowly; only wrap code likely to fail.
- On error, prefer logging (use `logging` over print for ops code).
- Never swallow exceptions unless absolutely justified; document if so.

### Docstrings/Documentation
- Docstrings are required for all public classes and functions.
- Use triple double-quoted strings; one-liners for simple functions, expanded style for complex APIs.
- Describe params and return values (Google or NumPy style preferred).

### Tests
- Test file names start with `test_` and live in the `tests/` folder.
- Use `pytest`-style fixtures and asserts whenever possible.
- Name test functions sequentially: `test_feature_scenario`.
- All logic must be tested for normal and edge cases.

### Miscellaneous
- Remove dead or commented code before commits.
- Avoid global mutable state.
- Use environment variables for config/secrets, never hard-code.
- Follow the AGENTS.md or .github/copilot-instructions.md as the primary rulebook. If conflicts, ask the user.

---

## 🔗 Special Instructions/Conventions
- If you encounter .cursor/rules/, .cursorrules, or .github/copilot-instructions.md, always incorporate relevant content here.
- Review this file each session: If unclear, ask for guidance.
- Stay current with master/main branch updates.

---

## 🤖 Agent Behavior Summary
- Be defensive, clear, and systematic.
- Make thorough plans and document rationale when unclear.
- Always prefer testable, maintainable solutions over clever/cryptic ones.
- Respect all business and technical guardrails described above.