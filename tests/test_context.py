"""Tests for the context module."""

from unittest.mock import MagicMock, patch

import pytest
from kit import Repository

from ai_pr_review.context import (
    add_diff_to_assembler,
    add_files_from_diff,
    extract_parent_symbols,
    initialize_repo_and_assembler,
    process_pr_context,
)


@pytest.fixture
def mock_repo():
    """Provide a mocked Kit Repository instance."""
    repo = MagicMock(spec=Repository)
    return repo


@pytest.fixture
def mock_assembler():
    """Provide a mocked context assembler."""
    assembler = MagicMock()
    return assembler


def test_initialize_repo_and_assembler():
    """Test initializing repository and context assembler."""
    with patch('ai_pr_review.context.Repository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_assembler = MagicMock()
        mock_repo.get_context_assembler.return_value = mock_assembler
        mock_repo_class.return_value = mock_repo

        repo, assembler = initialize_repo_and_assembler('/test/path')

        mock_repo_class.assert_called_once_with('/test/path')
        assert repo == mock_repo
        assert assembler == mock_assembler


def test_add_diff_to_assembler(mock_assembler):
    """Test adding diff text to the assembler."""
    diff_text = 'test diff content'

    add_diff_to_assembler(mock_assembler, diff_text)

    mock_assembler.add_diff.assert_called_once_with(diff_text)


def test_add_files_from_diff(mock_assembler):
    """Test adding files from diff to assembler."""
    with (
        patch('ai_pr_review.context.parse_patch') as mock_parse_patch,
        patch('ai_pr_review.context.os.path.exists') as mock_exists,
    ):
        # Setup mocks
        mock_diff_obj = MagicMock()
        mock_diff_obj.header.new_path = 'file.py'
        mock_diff_obj.header.old_path = 'file.py'
        mock_parse_patch.return_value = [mock_diff_obj]
        mock_exists.return_value = True

        # Test function
        add_files_from_diff(mock_assembler, '/test/path', 'diff content')

        # Assertions
        mock_parse_patch.assert_called_once_with('diff content')
        mock_assembler.add_file.assert_called_once_with('file.py')


def test_extract_parent_symbols(mock_repo, mock_assembler):
    """Test extracting parent symbols from diff."""
    with patch('ai_pr_review.context.parse_patch') as mock_parse_patch:
        # Setup mocks
        mock_diff_obj = MagicMock()
        mock_diff_obj.header.new_path = 'file.py'
        mock_diff_obj.header.old_path = 'file.py'

        mock_change = MagicMock()
        mock_change.hunk = 1
        mock_change.new = 10
        mock_diff_obj.changes = [mock_change]

        mock_parse_patch.return_value = [mock_diff_obj]

        parent_symbol_info = {
            'code': 'def test(): pass',
            'name': 'test',
            'start_line': 5,
        }
        mock_repo.extract_context_around_line.return_value = parent_symbol_info

        # Test function
        extract_parent_symbols(mock_assembler, mock_repo, '/test/path', 'diff content')

        # Assertions
        mock_repo.extract_context_around_line.assert_called_once_with('file.py', 9)
        mock_assembler.add_file.assert_called_once()


def test_process_pr_context():
    """Test the complete PR context processing workflow."""
    with (
        patch('ai_pr_review.context.initialize_repo_and_assembler') as mock_init,
        patch('ai_pr_review.context.add_diff_to_assembler') as mock_add_diff,
        patch('ai_pr_review.context.add_files_from_diff') as mock_add_files,
        patch('ai_pr_review.context.extract_parent_symbols') as mock_extract,
    ):
        # Setup mocks
        mock_repo = MagicMock()
        mock_assembler = MagicMock()
        mock_assembler.format_context.return_value = 'formatted context'
        mock_init.return_value = (mock_repo, mock_assembler)

        # Test function
        result = process_pr_context('/test/path', 'diff content')

        # Assertions
        mock_init.assert_called_once_with('/test/path')
        mock_add_diff.assert_called_once_with(mock_assembler, 'diff content')
        mock_add_files.assert_called_once_with(
            mock_assembler, '/test/path', 'diff content'
        )
        mock_extract.assert_called_once_with(
            mock_assembler, mock_repo, '/test/path', 'diff content'
        )
        mock_assembler.format_context.assert_called_once()
        assert result == 'formatted context'
