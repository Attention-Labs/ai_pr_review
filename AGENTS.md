# Repository Guidelines

- Run `uv run ruff check --fix src tests` before committing to ensure code style.
- Run `uv run pytest -q` to execute the test suite.
- Run `uv run -m ai_pr_review <repo_owner> <repo_name> <pr_number>` to review a PR.
- Run `uv run basedpyright` and resolve any reported issues before committing.
