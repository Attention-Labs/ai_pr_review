from __future__ import annotations

import os
from typing import List, Optional, cast

from kit import ContextAssembler, Repository
from whatthepatch import parse_patch
from whatthepatch.patch import Change, diffobj


def initialize_repo_and_assembler(
    repo_path: str,
) -> tuple[Repository, ContextAssembler]:
    """Initialize repository and context assembler."""
    repo = Repository(repo_path)
    return repo, repo.get_context_assembler()


def add_diff_to_assembler(assembler: ContextAssembler, diff_text: str) -> None:
    """Add diff to context assembler."""
    assembler.add_diff(diff_text)


def add_files_from_diff(
    assembler: ContextAssembler, temp_dir: str, diff_text: str
) -> None:
    """Add files from diff to context assembler."""
    parsed_diffs: list[diffobj] = list(parse_patch(diff_text))

    for diff_obj in parsed_diffs:
        if diff_obj.header is None:
            continue

        file_path_in_pr = diff_obj.header.new_path if diff_obj.header.new_path else None
        if file_path_in_pr is None:
            continue

        old_path = diff_obj.header.old_path if diff_obj.header.old_path else None
        is_removed_file = (file_path_in_pr == '/dev/null') or (
            old_path and not file_path_in_pr
        )

        if is_removed_file or not file_path_in_pr:
            continue

        try:
            full_path_on_disk = os.path.join(temp_dir, file_path_in_pr)
            if os.path.exists(full_path_on_disk):
                assembler.add_file(file_path_in_pr)
        except Exception:
            pass


def extract_parent_symbols(
    assembler: ContextAssembler, repo: Repository, temp_dir: str, diff_text: str
) -> None:
    """Extract parent symbols from changed lines for additional context."""
    parsed_diffs: list[diffobj] = list(parse_patch(diff_text))
    processed_parent_symbols: set[tuple[str, str | None, int | None]] = set()

    for diff_obj in parsed_diffs:
        if diff_obj.header is None:
            continue

        file_path_in_pr = diff_obj.header.new_path if diff_obj.header.new_path else None
        if file_path_in_pr is None:
            continue

        old_path = diff_obj.header.old_path if diff_obj.header.old_path else None
        is_removed_file = (file_path_in_pr == '/dev/null') or (
            old_path and not file_path_in_pr
        )

        if is_removed_file or not file_path_in_pr:
            continue

        hunks_data: dict[int, List[Change]] = {}
        if diff_obj.changes:
            for change in diff_obj.changes:
                if change.hunk not in hunks_data:
                    hunks_data[change.hunk] = []
                hunks_data[change.hunk].append(change)

        for _hunk_idx, changes_in_hunk in hunks_data.items():
            first_new_line_in_hunk: Optional[int] = None
            for ch in changes_in_hunk:
                if hasattr(ch, 'new') and ch.new is not None:
                    if (
                        first_new_line_in_hunk is None
                        or ch.new < first_new_line_in_hunk
                    ):
                        first_new_line_in_hunk = ch.new

            if first_new_line_in_hunk is not None:
                target_line_0_indexed = first_new_line_in_hunk - 1
                if target_line_0_indexed < 0:
                    continue

                try:
                    parent_symbol_info = repo.extract_context_around_line(
                        file_path_in_pr, target_line_0_indexed
                    )
                    if parent_symbol_info and parent_symbol_info.get('code'):
                        symbol_identifier = (
                            file_path_in_pr,
                            parent_symbol_info.get('name'),
                            parent_symbol_info.get('start_line'),
                        )
                        if symbol_identifier not in processed_parent_symbols:
                            parent_chunk = {
                                'code': parent_symbol_info['code'],
                                'path': file_path_in_pr,
                                'description': 'parent symbol context',
                            }
                            assembler.add_file(cast(str, parent_chunk))
                            processed_parent_symbols.add(symbol_identifier)
                except Exception:
                    pass


def process_pr_context(repo_path: str, diff_text: str) -> str:
    """Process PR diff and assemble context from changed files and relevant symbols."""
    repo, assembler = initialize_repo_and_assembler(repo_path)

    # Add diff to assembler
    add_diff_to_assembler(assembler, diff_text)

    # Add changed files to context
    add_files_from_diff(assembler, repo_path, diff_text)

    # Extract parent symbols for additional context
    extract_parent_symbols(assembler, repo, repo_path, diff_text)

    # Format and return the assembled context
    context = assembler.format_context()
    return context
