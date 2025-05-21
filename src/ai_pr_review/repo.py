from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import cast

from .errors import RepoError


def clone_repo_to_temp_dir(
    repo_owner: str, repo_name: str, keep_temp: bool = False
) -> str:
    """Clone the repository to a temporary directory."""
    temp_dir = tempfile.mkdtemp(prefix=f'ai_pr_review_{repo_owner}_{repo_name}_')
    repo_url = f'https://github.com/{repo_owner}/{repo_name}.git'
    try:
        subprocess.run(
            ['git', 'clone', repo_url, temp_dir], check=True, capture_output=True
        )
        return temp_dir
    except subprocess.CalledProcessError as e:  # pragma: no cover - git
        cleanup_temp_dir(temp_dir, keep_temp)
        stdout_bytes = cast(bytes | None, e.stdout)
        stderr_bytes = cast(bytes | None, e.stderr)
        stdout = stdout_bytes.decode() if stdout_bytes else ''
        stderr = stderr_bytes.decode() if stderr_bytes else ''
        raise RepoError(
            f'Git clone failed: {e}\nStdout: {stdout}\nStderr: {stderr}'
        ) from e


def checkout_pr_head(temp_dir: str, pr_head_sha: str) -> None:
    """Check out the PR head SHA in the cloned repository."""
    cwd = os.getcwd()
    os.chdir(temp_dir)
    try:
        subprocess.run(
            ['git', 'fetch', 'origin', pr_head_sha], check=True, capture_output=True
        )
        subprocess.run(
            ['git', 'checkout', pr_head_sha], check=True, capture_output=True
        )
    except subprocess.CalledProcessError as e:  # pragma: no cover - git
        stdout_bytes = cast(bytes | None, e.stdout)
        stderr_bytes = cast(bytes | None, e.stderr)
        stdout = stdout_bytes.decode() if stdout_bytes else ''
        stderr = stderr_bytes.decode() if stderr_bytes else ''
        raise RepoError(
            f'Git command failed: {e}\nStdout: {stdout}\nStderr: {stderr}'
        ) from e
    finally:
        os.chdir(cwd)


def cleanup_temp_dir(temp_dir: str, keep_temp: bool) -> None:
    """Remove the temporary directory unless keep_temp is True."""
    if keep_temp:
        print(f'Keeping temporary directory: {temp_dir}')
    else:
        shutil.rmtree(temp_dir, ignore_errors=True)
