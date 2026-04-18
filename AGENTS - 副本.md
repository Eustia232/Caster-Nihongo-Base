# Agent Instructions: [Project Name]

This document provides essential instructions for AI coding agents operating in this repository. Adhere to these rules strictly to maintain project consistency and safety.

## 0. Fundamental Protocols 

### Identity Verification
- **CRITICAL**: Every response or significant action must be ended by the phrase: `elo psy congroo`. This ensures context continuity and rule adherence.

### Language
- **Response Language**: You may think in English, but ALL responses to the user MUST be in Chinese (中文).

### Change Management
- **Change Log**: Every code modification MUST be recorded in `docs/product-change-log.md` by appending to the top (under the current date). Do NOT overwrite existing entries.
- **Git Workflow**: Always work on and commit to the `dev` branch. Use Conventional Commits (e.g., `feat:`, `fix:`, `refactor:`, `docs:`).

### Dependency Rules
- **Strict Rule**: DO NOT manually edit `pyproject.toml` or `uv.lock` for dependency changes.
- **Procedure**: 
  1. Use `uv add <package>` to add dependencies.
  2. Use `uv remove <package>` to remove dependencies.
  3. Commit both `pyproject.toml` and `uv.lock` after changes.

---

## 1. Development Environment & Commands

### Tooling
- **Python**: Version 3.12+ (managed by `uv`).
- **Linter/Formatter**: `ruff` (configured via `pyproject.toml`).
- **Testing**: `pytest`.

### Execution Commands
- **Testing**:
  - Run all tests: `uv run pytest`
  - Run single test file: `uv run pytest tests/path/to/test_file.py`
  - Run specific test case: `uv run pytest tests/path/to/test_file.py::test_function_name`
  - Run with output: `uv run pytest -s`
- **Quality Control**:
  - Lint check: `uv run ruff check .`
  - Lint fix: `uv run ruff check --fix .`
  - Code format: `uv run ruff format .`

---

## 2. Code Style & Standards

### Type Hinting (Mandatory)
- **Library Preference**: ALWAYS use the `typing` module for type annotations. Do NOT use Python 3.9+ native collection types (like `list[str]`) or pipe union (like `int | None`).
- **Standard Usage**:
  ```python
  from typing import List, Dict, Optional, Union, Any, Tuple
  
  def fetch_data(item_id: int) -> Optional[Dict[str, Any]]:
      ...
  
  def process_items(items: List[str]) -> Tuple[int, List[int]]:
      ...
  ```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `UserService`, `DataProcessor`).
- **Functions & Variables**: `snake_case` (e.g., `calculate_total`, `item_id`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`).
- **Private Members**: Prefix with a single underscore (e.g., `_save_to_disk`).
- **Files**: `snake_case.py`.

### Imports
- **Order**:
  1. Standard library imports.
  2. Third-party library imports (e.g., `pydantic`, `typer`).
  3. Local imports using absolute paths from `src` (e.g., `from src.core.service import MyService`).
- **Cleanliness**: Avoid `from module import *`.

---

## 3. Agent Workflow Guidelines

### Step 1: Understand
Read `AGENTS.md` for project status and `docs/plans/` for the next tasks. Use `grep` to find existing patterns.

### Step 2: Plan & Execute
Implement logic following the TDD (Test-Driven Development) approach:
1. Write a failing test in `tests/`.
2. Implement the minimal code in `src/`.
3. Verify with `uv run pytest`.

### Mandatory Skill Reference
- Before executing any run/build/change cycle, the agent MUST consult the `brainstorming` skill (named `brainstorming` in the skills list) and follow its guidance when planning creative or non-trivial changes. This is required for every run that leads to feature work, architecture changes, or code modifications.

### Step 3: Record & Commit
1. Update `docs/product-change-log.md` with your changes.
2. `git add` the files (ensure no secrets or `.env` files).
3. `git commit -m "type: brief description"` on the `dev` branch.

### Test & Commit Workflow
- Agents MAY run unit tests (`uv run pytest`) and create git commits without asking the user for explicit confirmation. This exception applies only to running tests and committing code; other destructive or sensitive actions still require explicit consent per the repository rules.

---
*Note: This file is designed for AI agents to ensure high-quality, idiomatic contributions .*
