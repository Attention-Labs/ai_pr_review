# Repository Guidelines

Use this file for a quick orientation to the repository and as a checklist
before committing changes.

## Key Directories

- `src/` – The `ai_pr_review` package with all source code.
- `tests/` – Pytest suite covering the package.
- `docs/` – Project documentation and design notes.
- `scripts/` – Utility scripts (e.g. `embed_repo.py` for vendoring code).
- `vendor/` – Third-party repos embedded here for offline tests and examples.

## Workflow
- Install the pre-commit hooks with `pre-commit install` to ensure `AGENTS.md` and `CLAUDE.md` stay synchronized and we only commit clean code.
- Run `uv run ruff check --fix src tests` before committing to ensure code style.
- Run `uv run pytest -q` to execute the test suite.
- Run `uv run -m ai_pr_review <repo_owner> <repo_name> <pr_number>` to review a PR.
- Run `uv run basedpyright` and resolve any reported issues before committing.
- Run `uv run -m ai_pr_review <repo_owner> <repo_name> <pr_number>` to review a PR.

If any directory layout or workflow step described here changes in a commit or
PR, update `AGENTS.md` as part of that same change so this file stays accurate.
