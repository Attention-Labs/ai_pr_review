from __future__ import annotations

import argparse
import sys
from typing import cast

from structlog.typing import FilteringBoundLogger

from logkit import capture, new_context
from logkit import log as _log  # type: ignore

from .errors import ReviewError
from .review import review_pr

log: FilteringBoundLogger = cast(FilteringBoundLogger, _log)


def main(cli_args: list[str] | None = None) -> None:
    """Entry point for the command line interface."""
    new_context(cmd='cli')
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
    parser.add_argument(
        '--model',
        default='gpt-4.1',
        help='OpenAI model to use for generating the review',
    )

    args = parser.parse_args(cli_args)
    try:
        with capture(cli='run'):
            review_text = review_pr(
                cast(str, args.repo_owner),
                cast(str, args.repo_name),
                cast(int, args.pr_number),
                cast(bool, args.keep_temp),
                cast(str, args.model),
            )
        print('\n--- AI PR Review (whatthepatch version) ---')
        print(review_text)
        print('--- End of AI PR Review ---')
    except ReviewError as exc:
        log.exception('review failed', exc_info=exc)
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
