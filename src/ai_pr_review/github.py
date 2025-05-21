from __future__ import annotations

import os
from typing import Any, Tuple, cast

import requests
from dotenv import load_dotenv

from .errors import GitHubError

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


def fetch_pr_data(
    repo_owner: str, repo_name: str, pr_number: int
) -> Tuple[str, str, str, str]:
    """Fetch diff text and metadata for the pull request."""
    base_url = (
        f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}'
    )
    headers: dict[str, str] = {}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'

    try:
        diff_headers = headers.copy()
        diff_headers['Accept'] = 'application/vnd.github.v3.diff'
        response_diff = requests.get(base_url, headers=diff_headers)
        response_diff.raise_for_status()
        diff_text = response_diff.text

        meta_headers = headers.copy()
        meta_headers['Accept'] = 'application/vnd.github.v3+json'
        response_meta = requests.get(base_url, headers=meta_headers)
        response_meta.raise_for_status()
        pr_metadata = cast(dict[str, Any], response_meta.json())
        head_sha = cast(str, pr_metadata['head']['sha'])
        pr_title = cast(str, pr_metadata.get('title', ''))
        pr_description = cast(str, pr_metadata.get('body', ''))
        return diff_text, head_sha, pr_title, pr_description
    except requests.exceptions.RequestException as e:  # pragma: no cover - network
        raise GitHubError(f'Error fetching PR data: {e}') from e
