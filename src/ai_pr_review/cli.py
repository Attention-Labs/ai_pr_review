from __future__ import annotations

import argparse
import sys

from .errors import ReviewError
from .review import review_pr


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
    try:
        review_text = review_pr(
            args.repo_owner, args.repo_name, args.pr_number, args.keep_temp
        )
        print('\n--- AI PR Review (whatthepatch version) ---')
        print(review_text)
        print('--- End of AI PR Review ---')
    except ReviewError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
