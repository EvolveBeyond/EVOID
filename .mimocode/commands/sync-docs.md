# Sync Documentation

Regenerate `arch.md`, `design.md`, and `agent.md` from current source code.

## Usage
```bash
python scripts/update_docs.py
```

## What it does
1. Scans all `evoid/**/*.py` files using AST parsing
2. Extracts: classes, functions, decorators, intent usage
3. Regenerates documentation with current timestamps
4. Updates version from `pyproject.toml`

## When to run
- After adding/removing classes or functions
- After changing intent definitions
- Before committing significant changes
- When pre-commit hook triggers on `evoid/*.py` changes
