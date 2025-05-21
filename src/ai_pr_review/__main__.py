import argparse
import os
import shutil
import subprocess
import tempfile

import requests
from dotenv import load_dotenv
from kit import Repository
from openai import OpenAI
from whatthepatch import parse_patch  # Changed from unidiff

load_dotenv()

# --- Configuration ---
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

if not OPENAI_API_KEY:
    print('Error: OPENAI_API_KEY environment variable not set.')
    exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)


# --- Helper Functions ---
def fetch_pr_data(repo_owner, repo_name, pr_number):
    """Fetches PR diff and head SHA."""
    print(f'Fetching PR data for {repo_owner}/{repo_name}/pull/{pr_number}...')
    base_url = (
        f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}'
    )
    headers = {}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'

    try:
        # Get Diff
        diff_headers = headers.copy()
        diff_headers['Accept'] = 'application/vnd.github.v3.diff'
        response_diff = requests.get(base_url, headers=diff_headers)
        response_diff.raise_for_status()
        diff_text = response_diff.text

        # Get Metadata (for head_sha)
        meta_headers = headers.copy()
        meta_headers['Accept'] = 'application/vnd.github.v3+json'
        response_meta = requests.get(base_url, headers=meta_headers)
        response_meta.raise_for_status()
        pr_metadata = response_meta.json()
        head_sha = pr_metadata['head']['sha']
        pr_title = pr_metadata.get('title', '')
        pr_description = pr_metadata.get('body', '')

        print(f'Successfully fetched PR data. Head SHA: {head_sha}')
        return diff_text, head_sha, pr_title, pr_description
    except requests.exceptions.RequestException as e:
        print(f'Error fetching PR data: {e}')
        if hasattr(e, 'response') and e.response is not None:
            print(f'Response content: {e.response.text}')
        exit(1)


def clone_repo_to_temp_dir(repo_owner, repo_name, keep_temp=False):
    """Clones the repository to a temporary directory."""
    print(f'Creating temporary directory for {repo_owner}/{repo_name}...')
    temp_dir = tempfile.mkdtemp(prefix=f'ai_pr_review_{repo_owner}_{repo_name}_')
    print(f'Temporary directory created: {temp_dir}')

    try:
        repo_url = f'https://github.com/{repo_owner}/{repo_name}.git'
        print(f'Cloning repository {repo_url}...')
        subprocess.run(
            ['git', 'clone', repo_url, temp_dir], check=True, capture_output=True
        )
        print(f'Successfully cloned repository to {temp_dir}')
        return temp_dir
    except subprocess.CalledProcessError as e:
        print(f'Git clone failed: {e}\nStdout: {e.stdout}\nStderr: {e.stderr}')
        cleanup_temp_dir(temp_dir, keep_temp)
        exit(1)


def checkout_pr_head(temp_dir, pr_head_sha):
    """Checks out the PR head SHA in the cloned repository."""
    cwd = os.getcwd()
    os.chdir(temp_dir)
    try:
        print(f'Fetching and checking out PR head SHA: {pr_head_sha}...')
        subprocess.run(
            ['git', 'fetch', 'origin', pr_head_sha], check=True, capture_output=True
        )
        subprocess.run(
            ['git', 'checkout', pr_head_sha], check=True, capture_output=True
        )
        print(f'Successfully checked out {pr_head_sha}.')
    except subprocess.CalledProcessError as e:
        print(f'Git command failed: {e}\nStdout: {e.stdout}\nStderr: {e.stderr}')
        exit(1)
    finally:
        os.chdir(cwd)


def cleanup_temp_dir(temp_dir, keep_temp):
    """Removes the temporary directory unless keep_temp is True."""
    if keep_temp:
        print(f'Keeping temporary directory: {temp_dir}')
    else:
        print(f'Removing temporary directory: {temp_dir}')
        shutil.rmtree(temp_dir, ignore_errors=True)


# --- Main Review Logic ---
def review_pr(repo_owner, repo_name, pr_number, keep_temp=False):
    temp_dir = None
    try:
        diff_text, head_sha, pr_title, pr_description = fetch_pr_data(
            repo_owner, repo_name, pr_number
        )

        # Clone repository to temporary directory
        temp_dir = clone_repo_to_temp_dir(repo_owner, repo_name, keep_temp)

        # Checkout PR head
        checkout_pr_head(temp_dir, head_sha)

        print('Initializing Kit Repository...')
        repo = Repository(temp_dir)
        assembler = repo.get_context_assembler()

        print('Building context for LLM using whatthepatch...')
        assembler.add_diff(diff_text)
        print('- Added raw diff to context.')

        parsed_diffs = list(parse_patch(diff_text))
        processed_parent_symbols = set()

        for diff_obj in parsed_diffs:
            # header.old_path, header.new_path
            # For deleted files, new_path is often /dev/null
            file_path_in_pr = diff_obj.header.new_path

            is_removed_file = (file_path_in_pr == '/dev/null') or (
                diff_obj.header.old_path and not file_path_in_pr
            )  # More robust check

            if is_removed_file:
                print(f'- Skipped removed file: {diff_obj.header.old_path}')
                continue

            if (
                not file_path_in_pr
            ):  # Should not happen if not removed, but as a safeguard
                print(
                    f'- Warning: No new_path for a non-removed file object '
                    f'(old: {diff_obj.header.old_path}). Skipping.'
                )
                continue

            # 2. Add full content of changed files
            try:
                full_path_on_disk = os.path.join(temp_dir, file_path_in_pr)
                if os.path.exists(full_path_on_disk):
                    assembler.add_file(file_path_in_pr)
                    print(f'- Added full content of changed file: {file_path_in_pr}')
                else:
                    print(
                        f'- Warning: Changed file {file_path_in_pr} not found on disk '
                        f'at {full_path_on_disk}. Diff will be primary source.'
                    )
            except Exception as e:
                print(
                    f'- Error adding file {file_path_in_pr} to context: {e}. '
                    f'Diff will be primary source.'
                )

            # 3. Add parent symbol of each changed hunk
            # Group changes by hunk index
            hunks_data = {}  # Key: hunk_index, Value: list of Change objects
            if diff_obj.changes:  # Ensure there are changes
                for change in diff_obj.changes:
                    # change: namedtuple (old_line_no, new_line_no, line_content, hunk_no)
                    if change.hunk not in hunks_data:
                        hunks_data[change.hunk] = []
                    hunks_data[change.hunk].append(change)

            for hunk_idx, changes_in_hunk in hunks_data.items():
                # Find the first line number in the *new* file for this hunk
                first_new_line_in_hunk = None
                for ch in changes_in_hunk:
                    if ch.new is not None:  # Line exists in the new file
                        if (
                            first_new_line_in_hunk is None
                            or ch.new < first_new_line_in_hunk
                        ):
                            first_new_line_in_hunk = ch.new

                if first_new_line_in_hunk is not None:
                    # whatthepatch line numbers are 1-indexed
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
                                symbol_name = parent_symbol_info.get(
                                    'name', 'Unnamed Symbol'
                                )
                                start_line = parent_symbol_info.get('start_line', '?')
                                end_line = parent_symbol_info.get('end_line', '?')
                                chunk_description = (
                                    f"Context: Symbol '{symbol_name}' "
                                    f'in {file_path_in_pr} (lines {start_line}-{end_line}) '
                                    f'related to changes starting around line {first_new_line_in_hunk} '
                                    f'in the new file.'
                                )
                                parent_chunk = {
                                    'code': parent_symbol_info['code'],
                                    'path': file_path_in_pr,
                                    'description': chunk_description,
                                }
                                assembler.add_file(parent_chunk)
                                processed_parent_symbols.add(symbol_identifier)
                                symbol_name = parent_symbol_info.get('name', 'Unnamed')
                                print(
                                    f'  - Added parent symbol context: {symbol_name} '
                                    f'from {file_path_in_pr} for hunk {hunk_idx}'
                                )
                    except Exception as e:
                        print(
                            f'  - Error extracting parent symbol for hunk {hunk_idx} '
                            f'in {file_path_in_pr}: {e}'
                        )

        context_blob = assembler.format_context()
        print(f'\nContext assembled. Total length: {len(context_blob)} characters.')
        # with open("context_blob_whatthepatch.txt", "w") as f:
        #     f.write(context_blob)
        # print("Context blob saved to context_blob_whatthepatch.txt")

        print('\nSending context to LLM for review...')
        system_prompt = (
            'You are an expert software engineer performing a pull request review. '
            'Focus on correctness, clarity, potential bugs, '
            'adherence to best practices, and areas for improvement. '
            'Be concise and actionable. '
            'Structure your review clearly, perhaps by file or by general concern. '
            'If you suggest code changes, use markdown code blocks.'
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
            max_tokens=2000,  # Increased slightly for potentially richer context
        )
        review_text = llm_response.choices[0].message.content

        print('\n--- AI PR Review (whatthepatch version) ---')
        print(review_text)
        print('--- End of AI PR Review ---')

    finally:
        if temp_dir:
            cleanup_temp_dir(temp_dir, keep_temp)


def main(cli_args: list[str] | None = None) -> None:
    """Entry point for the command line interface."""
    parser = argparse.ArgumentParser(
        description='AI PR Reviewer using Kit and whatthepatch (Version 1)'
    )
    parser.add_argument(
        'repo_owner', help="Owner of the GitHub repository (e.g., 'octocat')"
    )
    parser.add_argument(
        'repo_name', help="Name of the GitHub repository (e.g., 'Spoon-Knife')"
    )
    parser.add_argument('pr_number', type=int, help='Pull Request number')
    parser.add_argument(
        '--keep-temp',
        action='store_true',
        help='Keep the temporary repository after execution (for debugging)',
    )

    args = parser.parse_args(cli_args)
    review_pr(args.repo_owner, args.repo_name, args.pr_number, args.keep_temp)


if __name__ == '__main__':
    main()
