# Agent Instructions: Caster-Nihongo-Base

This document provides essential instructions for AI coding agents operating in this repository. Adhere to these rules strictly to maintain project consistency and safety.

## 0. Fundamental Protocols 

### Identity Verification
- **CRITICAL**: Every response or significant action must be ended by the phrase: `elo psy congroo`. This ensures context continuity and rule adherence.

### Change Management
- **Change Log**: Every code modification MUST be recorded in `product-change-log.md` by appending to the top (under the current date). Do NOT overwrite existing entries.
- **Git Workflow**: Always work on and commit to the `dev` branch. Use Conventional Commits (e.g., `feat:`, `fix:`, `refactor:`, `docs:`).

### Dependency Rules
- **Strict Rule**: DO NOT use `uv add`.
- **Procedure**: 
  1. Manually edit the `dependencies` list in `pyproject.toml`.
  2. Run `uv sync` to update the lockfile and environment.
  3. Commit both `pyproject.toml` and `uv.lock`.

---

## 1. Development Environment & Commands

### Tooling
- **Python**: Version 3.12+ (managed by `uv`).
- **Linter/Formatter**: `ruff` (configured via `pyproject.toml`).
- **Testing**: `pytest`.

### Execution Commands
- **Run Application**: 
  - `uv run main.py import`
  - `uv run main.py review`
  - `uv run main.py export`
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
  
  def get_word(word_id: int) -> Optional[Dict[str, Any]]:
      ...
  
  def process_list(items: List[str]) -> Tuple[int, List[int]]:
      ...
  ```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `WordRepository`, `FSRSEngine`).
- **Functions & Variables**: `snake_case` (e.g., `calculate_next_interval`, `word_id`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_STABILITY`).
- **Private Members**: Prefix with a single underscore (e.g., `_save_to_disk`).
- **Files**: `snake_case.py`.

### Imports
- **Order**:
  1. Standard library imports.
  2. Third-party library imports (e.g., `pydantic`, `fsrs`).
  3. Local imports using absolute paths from `src` (e.g., `from src.core.logic import ReviewSession`).
- **Cleanliness**: Avoid `from module import *`.

### Error Handling
- **Custom Exceptions**: Define specific exceptions in `src/core/exceptions.py`.
- **Logic Layer**: Raise descriptive exceptions instead of returning `None` or printing errors.
- **CLI Layer**: Catch exceptions and use `Rich` to display user-friendly error messages.

### Data Modeling (Pydantic V2)
- Use `pydantic.BaseModel` for all data structures.
- Use `Field` with `description` for clarity.
- Ensure models in `src/data/models.py` are compatible with YAML (for `words.yaml`) and JSON (for `progress.json`).

---

## 3. Architecture Overview

The project follows a decoupled layered architecture:

1.  **Interface Layer (`src/cli/`)**: Handles `Typer` commands and `Rich` terminal rendering. No business logic should reside here.
2.  **Service/Logic Layer (`src/core/`)**: Contains the FSRS algorithm, word deduplication, and file processing logic.
3.  **Data/Persistence Layer (`src/data/`)**: Manages Pydantic models and file I/O (Repository pattern).
4.  **Storage (`data_store/`)**: Contains `words.yaml` (static word data) and `progress.json` (FSRS state).

---

## 4. Agent Workflow Guidelines

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
1. Update `product-change-log.md` with your changes.
2. `git add` the files (ensure no secrets or `.env` files).
3. `git commit -m "type: brief description"` on the `dev` branch.

### Test & Commit Workflow
- Agents MAY run unit tests (`uv run pytest`) and create git commits without asking the user for explicit confirmation. This exception applies only to running tests and committing code; other destructive or sensitive actions still require explicit consent per the repository rules.

---
*Note: This file is designed for AI agents to ensure high-quality, idiomatic contributions .*
