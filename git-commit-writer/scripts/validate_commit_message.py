#!/usr/bin/env python3
"""Validate a commit message against the git-commit-writer policy."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PREFERRED_LINE_LENGTH = 78
MAX_LINE_LENGTH = 80
SUBJECT_RE = re.compile(
    r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)"
    r"\([a-z0-9][a-z0-9._-]*\)!?: [a-z0-9].*[^.]$"
)
FORBIDDEN_RE = re.compile(
    r"(?i)(co-authored-by|generated-(?:by|with)|"
    r"(?:claude|chatgpt|codex|copilot|gemini).*(?:generated|authored))"
)


def read_message(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def validate(message: str) -> list[str]:
    errors: list[str] = []

    try:
        message.encode("ascii")
    except UnicodeEncodeError as exc:
        errors.append(f"message contains non-ASCII text near character {exc.start + 1}")

    lines = message.rstrip("\n").splitlines()
    if not lines or not lines[0]:
        return errors + ["subject is missing"]

    for number, line in enumerate(lines, start=1):
        if len(line) > MAX_LINE_LENGTH:
            errors.append(
                f"line {number} is {len(line)} characters; maximum is "
                f"{MAX_LINE_LENGTH}"
            )
        if line.rstrip() != line:
            errors.append(f"line {number} has trailing whitespace")

    subject = lines[0]
    if not SUBJECT_RE.fullmatch(subject):
        errors.append(
            "subject must match 'type(scope): description' with an allowed type, "
            "a lowercase scope, an imperative lowercase description, and no period"
        )

    if len(lines) < 3 or lines[1] != "" or not lines[2].strip():
        errors.append("a non-empty body must follow the subject after one blank line")

    match = FORBIDDEN_RE.search(message)
    if match:
        errors.append(f"forbidden attribution found: {match.group(0)!r}")

    return errors


def warnings(message: str) -> list[str]:
    notices: list[str] = []

    for number, line in enumerate(message.rstrip("\n").splitlines(), start=1):
        if PREFERRED_LINE_LENGTH < len(line) <= MAX_LINE_LENGTH:
            notices.append(
                f"line {number} is {len(line)} characters; prefer "
                f"{PREFERRED_LINE_LENGTH} or fewer"
            )

    return notices


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message", help="commit message file, or - for standard input")
    args = parser.parse_args()

    try:
        message = read_message(args.message)
    except (OSError, UnicodeError) as exc:
        print(f"error: cannot read commit message: {exc}", file=sys.stderr)
        return 2

    errors = validate(message)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    for notice in warnings(message):
        print(f"warning: {notice}", file=sys.stderr)

    print("Commit message is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
