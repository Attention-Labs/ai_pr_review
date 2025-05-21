# AI PR Review

An AI-powered pull request review tool that helps developers get quick, high-quality feedback on their GitHub pull requests.

## Overview

AI PR Review analyzes GitHub pull requests and provides detailed feedback using large language models. It examines code changes, surrounding context, and PR metadata to generate helpful reviews focused on:

- Code correctness
- Potential bugs and edge cases
- Best practices and patterns
- Clarity and maintainability
- Suggested improvements

## Features

- Fetches PR data directly from GitHub
- Analyzes both the diff and full file context
- Understands code at the symbol level (functions, classes, etc.)
- Provides actionable, specific feedback
- Works with any GitHub repository

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and add your API keys
3. Install dependencies: `uv sync --all-extras`
4. Set up pre-commit hooks: `pre-commit install`

## Usage

```bash
python -m ai_pr_review [--model MODEL] <repo_owner> <repo_name> <pr_number>
```
Use `--model` to choose the OpenAI model (defaults to `gpt-4.1`).

Example:
```bash
python -m ai_pr_review octocat hello-world 42
```

## Requirements

- Python 3.11+
- GitHub access token (optional but recommended)
- OpenAI API key

## License

[MIT](LICENSE)