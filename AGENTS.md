# AGENTS Guidance

This repository hosts an AI-powered tool for reviewing GitHub pull requests.

## Running the CLI
Use the module entrypoint to generate a review:

```bash
uv run python -m ai_pr_review <repo_owner> <repo_name> <pr_number>
```

## Running the Tests
Execute the full test suite with:

```bash
uv run pytest
```

## Pre-commit Hooks
Formatting, linting and type checks are managed by pre-commit. Run all hooks on the codebase with:

```bash
uv run pre-commit run --all-files
```

## Linting Only
To run the linters directly:

```bash
uv run ruff check .
uv run pyright
```

