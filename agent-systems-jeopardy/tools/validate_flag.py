#!/usr/bin/env python3
"""Validate a flag candidate against the competition regex.

Used by ctf-verifier before writing flag.txt. Exit 0 = valid match (prints the
cleaned flag), exit 1 = no match.

Usage:
    python3 tools/validate_flag.py '<candidate>'
    python3 tools/validate_flag.py --regex 'FLAG\\{[^}]+\\}' '<candidate>'
    echo '<candidate>' | python3 tools/validate_flag.py -
"""
import argparse
import re
import sys

DEFAULT_REGEX = r"ctfcup\{[^}]+\}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate", help="flag candidate or '-' for stdin")
    ap.add_argument("--regex", default=DEFAULT_REGEX,
                    help="competition flag regex (default: ctfcup{...})")
    args = ap.parse_args()

    data = sys.stdin.read() if args.candidate == "-" else args.candidate
    matches = re.findall(args.regex, data)
    if not matches:
        print("NO MATCH", file=sys.stderr)
        sys.exit(1)
    # de-dup preserving order
    seen = []
    for m in matches:
        if m not in seen:
            seen.append(m)
    if len(seen) > 1:
        print(f"WARNING: {len(seen)} distinct matches", file=sys.stderr)
    for m in seen:
        print(m)
    sys.exit(0)


if __name__ == "__main__":
    main()
