#!/usr/bin/env python3
"""Validate a flag candidate against the flag format defined in current-state.md.

Usage:
    tools/flag_check.py <candidate> [--state state/<task-slug>/current-state.md]

Behavior:
    - Reads `Flag format:` line from current-state.md (default regex: ctfcup\{[^}]+\}).
    - Searches candidate for a match.
    - On match: prints the matched substring to stdout and exits 0.
    - On no match: prints nothing and exits 1.

Design notes:
    - Candidate may be messy (multi-line stdout from gdb/volatility). We re.search,
      not re.fullmatch. That is intentional — the regex itself anchors the format.
    - We never auto-write flag.txt from here. That is ctf-verifier's job.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_FLAG_REGEX = r"ctfcup\{[^}]+\}"


def read_flag_format(state_path: Path | None) -> str:
    if state_path is None or not state_path.exists():
        return DEFAULT_FLAG_REGEX
    for raw in state_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.lower().startswith("flag format:"):
            value = line.split(":", 1)[1].strip()
            # strip optional backticks or quotes
            value = value.strip("`\"' ")
            if value:
                return value
    return DEFAULT_FLAG_REGEX


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate flag candidate.")
    parser.add_argument("candidate", help="Candidate string (may be multi-line).")
    parser.add_argument(
        "--state",
        default=None,
        help="Path to current-state.md with `Flag format:` line.",
    )
    args = parser.parse_args()

    state_path = Path(args.state) if args.state else None
    regex = read_flag_format(state_path)

    try:
        pattern = re.compile(regex)
    except re.error as exc:
        print(f"[flag_check] invalid regex {regex!r}: {exc}", file=sys.stderr)
        return 2

    match = pattern.search(args.candidate)
    if match is None:
        return 1

    print(match.group(0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
