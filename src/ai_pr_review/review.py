from __future__ import annotations

import os

from dotenv import load_dotenv
from kit import Repository
from openai import OpenAI
from whatthepatch import parse_patch

from .errors import ConfigurationError
from .github import fetch_pr_data
from .repo import checkout_pr_head, cleanup_temp_dir, clone_repo_to_temp_dir

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ConfigurationError('OPENAI_API_KEY environment variable not set.')

client = OpenAI(api_key=OPENAI_API_KEY)


def review_pr(
    repo_owner: str, repo_name: str, pr_number: int, keep_temp: bool = False
) -> str:
    """Generate an AI-based review for the pull request."""
    temp_dir: str | None = None
    try:
        diff_text, head_sha, pr_title, pr_description = fetch_pr_data(
            repo_owner, repo_name, pr_number
        )
        temp_dir = clone_repo_to_temp_dir(repo_owner, repo_name, keep_temp)
        checkout_pr_head(temp_dir, head_sha)

        repo = Repository(temp_dir)
        assembler = repo.get_context_assembler()
        assembler.add_diff(diff_text)

        parsed_diffs = list(parse_patch(diff_text))
        processed_parent_symbols: set[tuple[str, str | None, int | None]] = set()
        for diff_obj in parsed_diffs:
            file_path_in_pr = diff_obj.header.new_path
            is_removed_file = (file_path_in_pr == '/dev/null') or (
                diff_obj.header.old_path and not file_path_in_pr
            )
            if is_removed_file:
                continue
            if not file_path_in_pr:
                continue
            try:
                full_path_on_disk = os.path.join(temp_dir, file_path_in_pr)
                if os.path.exists(full_path_on_disk):
                    assembler.add_file(file_path_in_pr)
            except Exception:
                pass
            hunks_data: dict[int, list] = {}
            if diff_obj.changes:
                for change in diff_obj.changes:
                    if change.hunk not in hunks_data:
                        hunks_data[change.hunk] = []
                    hunks_data[change.hunk].append(change)

            for _hunk_idx, changes_in_hunk in hunks_data.items():
                first_new_line_in_hunk = None
                for ch in changes_in_hunk:
                    if ch.new is not None:
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
                                assembler.add_file(parent_chunk)
                                processed_parent_symbols.add(symbol_identifier)
                    except Exception:
                        pass

        context_blob = assembler.format_context()
        system_prompt = (
            'You are an expert software engineer performing a pull request review. '
            'Focus on correctness, clarity, potential bugs, adherence to best practices, '
            'and areas for improvement. Be concise and actionable.'
        )
        user_prompt = (
            f'Please review the following pull request.\n\n'
            f'PR Title: {pr_title}\n'
            f'PR Description:\n{pr_description or "No description provided."}\n\n'
            f'Context (Diff, changed files, and relevant symbols):\n'
            f'```\n{context_blob}\n```\n\n'
            f'Provide your review:'
        )

        llm_response = client.chat.completions.create(
            model='gpt-4.1',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            temperature=0.2,
            max_tokens=2000,
        )
        review_text = llm_response.choices[0].message.content
        return review_text
    finally:
        if temp_dir:
            cleanup_temp_dir(temp_dir, keep_temp)
