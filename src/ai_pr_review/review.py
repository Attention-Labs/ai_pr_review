from __future__ import annotations

from .context import process_pr_context
from .github import fetch_pr_data
from .llm import review_with_llm
from .repo import checkout_pr_head, cleanup_temp_dir, clone_repo_to_temp_dir


def review_pr(
    repo_owner: str, repo_name: str, pr_number: int, keep_temp: bool = False
) -> str:
    """Generate an AI-based review for the pull request."""
    temp_dir: str | None = None
    try:
        # Fetch PR data from GitHub
        diff_text, head_sha, pr_title, pr_description = fetch_pr_data(
            repo_owner, repo_name, pr_number
        )

        # Clone repository and checkout PR head
        temp_dir = clone_repo_to_temp_dir(repo_owner, repo_name, keep_temp)
        checkout_pr_head(temp_dir, head_sha)

        # Generate context from PR diff and files
        context_blob = process_pr_context(temp_dir, diff_text)

        # Generate PR review using LLM
        review_text = review_with_llm(pr_title, pr_description, context_blob)

        return review_text
    finally:
        if temp_dir:
            cleanup_temp_dir(temp_dir, keep_temp)
