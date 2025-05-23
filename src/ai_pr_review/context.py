from __future__ import annotations

import os
from typing import Any, Optional, Set, cast

from kit import Repository
from whatthepatch import parse_patch
from whatthepatch.patch import Change


class _MiniHunk:
    def __init__(self, target_start: int):
        self.target_start = target_start


class _MiniPatchFile:
    def __init__(self, path: str, removed: bool, hunks: list[_MiniHunk]):
        self.path = path
        self.is_removed_file = removed
        self._hunks = hunks

    def __iter__(self):
        return iter(self._hunks)


def _parse_patchset(diff_text: str) -> list[_MiniPatchFile]:
    files: list[_MiniPatchFile] = []
    for diff in parse_patch(diff_text):
        if diff.header is None:
            continue

        new_path = diff.header.new_path
        old_path = diff.header.old_path
        file_path = new_path or old_path
        removed = (new_path in (None, '/dev/null')) or (bool(old_path) and not new_path)

        hunks: dict[int, list[Change]] = {}
        if diff.changes:
            for ch in diff.changes:
                hunks.setdefault(ch.hunk, []).append(ch)

        parsed_hunks: list[_MiniHunk] = []
        for changes in hunks.values():
            target_start: int | None = None
            for ch in changes:
                if ch.new is not None and (
                    target_start is None or ch.new < target_start
                ):
                    target_start = ch.new
            if target_start is not None:
                parsed_hunks.append(_MiniHunk(target_start))

        if file_path:
            files.append(_MiniPatchFile(file_path, removed, parsed_hunks))

    return files


def _safe_parent_context(
    repo: Repository, file_path: str, one_based_line: int
) -> Optional[dict[str, Any]]:
    """Return a {'name', 'code', 'start_line'} dict for the symbol that
    encloses `one_based_line` in `file_path`, or None if not found."""
    try:
        return repo.extract_context_around_line(file_path, one_based_line - 1)
    except Exception:
        return None


def process_pr_context(repo_path: str, diff_text: str) -> str:
    """Build an LLM-ready context string for a PR diff."""
    repo = Repository(repo_path)
    assembler = repo.get_context_assembler()

    # 1️⃣  Raw diff – always first so the model sees the exact edits.
    assembler.add_diff(diff_text)

    patch = _parse_patchset(diff_text)

    seen_files: Set[str] = set()
    touched_symbols: Set[str] = set()

    for pfile in patch:
        if pfile.is_removed_file:
            continue

        file_path = pfile.path
        if not file_path:
            continue

        if file_path not in seen_files and os.path.exists(
            os.path.join(repo_path, file_path)
        ):
            assembler.add_file(file_path, highlight_changes=True, max_lines=400)
            add_deps = getattr(assembler, 'add_symbol_dependencies', None)
            if callable(add_deps):
                add_deps(file_path, max_depth=1)
            seen_files.add(file_path)

        hunk = next(iter(pfile), None)
        if hunk and hunk.target_start:
            parent_ctx = _safe_parent_context(repo, file_path, hunk.target_start)
            if parent_ctx and parent_ctx.get('code'):
                assembler.add_search_results(
                    [{'file': file_path, 'code': parent_ctx['code']}],
                    query='parent symbol context',
                )
                if parent_ctx.get('name'):
                    touched_symbols.add(cast(str, parent_ctx['name']))

    for sym_name in touched_symbols:
        try:
            usages = repo.find_symbol_usages(sym_name)
        except Exception:
            usages = []

        for u in usages[:20]:
            u_file = u.get('file')
            u_line = u.get('line_number')
            snippet = u.get('snippet') or u.get('line')
            if not (u_file and snippet):
                continue

            usage_blob = f'# Usage of `{sym_name}` at {u_file}:{u_line}\n{cast(str, snippet).rstrip()}'
            assembler.add_search_results(
                [{'file': u_file, 'code': usage_blob}],
                query=f'usage of {sym_name}',
            )

    return assembler.format_context()
