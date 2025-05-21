import subprocess

import pytest

from ai_pr_review.cli import main as cli_main
from ai_pr_review.errors import GitHubError, RepoError, ReviewError
from ai_pr_review.github import fetch_pr_data
from ai_pr_review.repo import clone_repo_to_temp_dir


def test_fetch_pr_data_error(monkeypatch):
    def raise_request(*_a, **_kw):
        raise requests.exceptions.RequestException('boom')

    import requests

    monkeypatch.setattr(requests, 'get', raise_request)
    with pytest.raises(GitHubError):
        fetch_pr_data('o', 'r', 1)


def test_clone_repo_to_temp_dir_error(monkeypatch):
    def run_fail(*args, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=1, cmd=args[0], output=b'', stderr=b''
        )

    monkeypatch.setattr(subprocess, 'run', run_fail)
    with pytest.raises(RepoError):
        clone_repo_to_temp_dir('o', 'r')


def test_cli_catches_review_error(monkeypatch):
    def raise_error(*_a, **_kw):
        raise ReviewError('boom')

    monkeypatch.setattr('ai_pr_review.cli.review_pr', raise_error)
    with pytest.raises(SystemExit) as exc:
        cli_main(['o', 'r', '1'])
    assert exc.value.code == 1
