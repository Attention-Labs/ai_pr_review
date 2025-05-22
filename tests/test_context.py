"""Tests for the context module."""

from unittest.mock import MagicMock

import pytest

from ai_pr_review.context import _safe_parent_context, process_pr_context


@pytest.mark.parametrize(
    'exc',
    [None, Exception('boom')],
)
def test_safe_parent_context(exc):
    repo = MagicMock()
    if exc:
        repo.extract_context_around_line.side_effect = exc
    else:
        repo.extract_context_around_line.return_value = {
            'name': 'f',
            'code': 'x',
            'start_line': 1,
        }

    result = _safe_parent_context(repo, 'f.py', 3)
    if exc:
        assert result is None
    else:
        assert result == {'name': 'f', 'code': 'x', 'start_line': 1}


def test_process_pr_context_integration():
    diff_text = (
        'diff --git a/src/whatthepatch/__init__.py b/src/whatthepatch/__init__.py\n'
        'index 0000000..1111111 100644\n'
        '--- a/src/whatthepatch/__init__.py\n'
        '+++ b/src/whatthepatch/__init__.py\n'
        '@@\n'
        ' from .patch import parse_patch\n'
        ' from .apply import apply_diff\n'
        ' \n'
        ' __all__ = ["parse_patch", "apply_diff"]\n'
        '+\n'
        '+VERSION = "0.0.0"\n'
    )

    result = process_pr_context('vendor/whatthepatch', diff_text)
    assert 'VERSION = "0.0.0"' in result
    assert diff_text.splitlines()[0] in result
