#!/usr/bin/env python3
"""Pre-commit hook to sync AGENTS.md and CLAUDE.md."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_FILE = REPO_ROOT / "AGENTS.md"
CLAUDE_FILE = REPO_ROOT / "CLAUDE.md"


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _staged_files() -> set[str]:
    out = _run(["git", "diff", "--name-only", "--cached"])
    return set(out.splitlines())


def _stage(path: Path) -> None:
    relative = path.relative_to(REPO_ROOT)
    subprocess.run(["git", "add", str(relative)], check=True)


def _read(path: Path) -> str:
    return path.read_text()


def _sync(src: Path, dest: Path) -> None:
    dest.write_text(_read(src))
    _stage(dest)
    print(f"Synced {src.name} -> {dest.name}")


def main() -> int:
    changed = _staged_files()
    agent_changed = str(AGENTS_FILE.relative_to(REPO_ROOT)) in changed
    claude_changed = str(CLAUDE_FILE.relative_to(REPO_ROOT)) in changed

    agent_content = _read(AGENTS_FILE)
    claude_content = _read(CLAUDE_FILE)

    if agent_changed and claude_changed:
        if agent_content != claude_content:
            sys.stderr.write(
                "Both AGENTS.md and CLAUDE.md changed with different content."
                " Commit one file at a time to keep them in sync.\n"
            )
            return 1
        return 0

    if agent_changed:
        if agent_content != claude_content:
            _sync(AGENTS_FILE, CLAUDE_FILE)
        return 0

    if claude_changed:
        if agent_content != claude_content:
            _sync(CLAUDE_FILE, AGENTS_FILE)
        return 0

    if agent_content != claude_content:
        sys.stderr.write(
            "AGENTS.md and CLAUDE.md differ but neither file was staged."
            " Please update one file so they match.\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
