# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI PR Review is a tool that uses AI to review GitHub pull requests. It:
1. Fetches PR data (diff, metadata) from GitHub's API
2. Clones the repository to a temporary directory
3. Extracts context from the changed files and surrounding code
4. Sends the context to an LLM (currently GPT-4.1) for review
5. Displays the AI-generated PR review

## Dependencies

The project uses:
- Python 3.11+
- cased-kit: For code context extraction
- openai: For LLM API access
- whatthepatch: For parsing git diff format
- python-dotenv: For environment variable management
- requests: For GitHub API calls

## Setup and Configuration

1. Copy `.env.example` to `.env` and add:
   - `OPENAI_API_KEY`: Required for LLM access
   - `GITHUB_TOKEN`: Optional but recommended for GitHub API access (avoids rate limits)

## Running the Tool

Basic usage:
```bash
python main.py <repo_owner> <repo_name> <pr_number>
```

Example:
```bash
python main.py anthropics claude-code 123
```

Options:
- `--keep-temp`: Keep the temporary repository clone after execution (useful for debugging)

## Code Architecture

The main components are:
1. **GitHub PR Data Fetching**: Functions to fetch PR diff and metadata using GitHub API
2. **Repository Management**: Functions to clone, checkout, and clean up temporary repos
3. **Context Extraction**: Uses Kit's context assembler and whatthepatch to build context from changes
4. **LLM Processing**: Formats context with prompts and sends to LLM for review

## Development Notes

- Use Python's virtual environment capabilities for development
- Install dependencies using a package manager like pip, poetry, or uv
- The project uses [Kit](https://github.com/cased/kit) for code context extraction
- PR reviews focus on correctness, clarity, potential bugs, and best practices