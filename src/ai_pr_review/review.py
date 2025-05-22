from __future__ import annotations

from typing import Callable

from logkit import capture, log

from .context import process_pr_context
from .github import fetch_pr_data
from .llm import review_with_llm
from .repo import checkout_pr_head, cleanup_temp_dir, clone_repo_to_temp_dir


def review_pr(
    repo_owner: str,
    repo_name: str,
    pr_number: int,
    keep_temp: bool = False,
    model: str = 'gpt-4.1',
    *,
    fetch_pr_data_func: Callable[
        [str, str, int], tuple[str, str, str, str]
    ] = fetch_pr_data,
    clone_repo_func: Callable[[str, str, bool], str] = clone_repo_to_temp_dir,
    checkout_func: Callable[[str, str], None] = checkout_pr_head,
    process_context_func: Callable[[str, str], str] = process_pr_context,
    review_with_llm_func: Callable[..., str] = review_with_llm,
    cleanup_func: Callable[[str, bool], None] = cleanup_temp_dir,
) -> str:
    """Generate an AI-based review for the pull request."""
    temp_dir: str | None = None
    review_text: str | None = None
    with capture(work='review_pr'):
        try:
            # Fetch PR data from GitHub
            diff_text, head_sha, pr_title, pr_description = fetch_pr_data_func(
                repo_owner, repo_name, pr_number
            )
            log.info('fetched pr data', owner=repo_owner, repo=repo_name)

            # Clone repository and checkout PR head
            temp_dir = clone_repo_func(repo_owner, repo_name, keep_temp)
            log.info('cloned repo', path=temp_dir)
            checkout_func(temp_dir, head_sha)

            # Generate context from PR diff and files
            context_blob = process_context_func(temp_dir, diff_text)
            log.info('processed context')

            # Generate PR review using LLM
            review_text = review_with_llm_func(
                pr_title,
                pr_description,
                context_blob,
                model=model,
            )
            log.info('generated review')
        finally:
            if temp_dir:
                cleanup_func(temp_dir, keep_temp)
    assert review_text is not None
    return review_text
