#!/usr/bin/env python3
"""Validate and serialize the upstream skill configuration."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


NAME_RE = re.compile(r"[a-z0-9][a-z0-9._-]*")
ALLOWED_FIELDS = {"target_path", "repository", "ref", "source_path"}


def require_string(name: str, field: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"skill {name} has invalid {field}")
    if any(character.isspace() for character in value):
        raise ValueError(
            f"skill {name} {field} contains unsupported whitespace"
        )
    return value


def validate_path(name: str, field: str, value: str, allow_dot: bool) -> None:
    path = PurePosixPath(value)

    if value == "." and allow_dot:
        return
    if value in ("", ".") or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"invalid {field} for skill {name}")


def load_upstreams(path: Path) -> list[dict[str, str]]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path.name}: {exc}") from exc

    if not isinstance(config, dict):
        raise ValueError("upstreams.json must contain an object")
    if not config:
        raise ValueError("upstreams.json contains no skills")

    seen_target_paths: set[str] = set()
    records: list[dict[str, str]] = []

    for name, skill in config.items():
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            raise ValueError(f"invalid skill name: {name}")
        if not isinstance(skill, dict):
            raise ValueError(f"skill {name} must be an object")

        unknown_fields = set(skill) - ALLOWED_FIELDS
        if unknown_fields:
            fields = ", ".join(sorted(unknown_fields))
            raise ValueError(f"skill {name} has unknown fields: {fields}")

        repository = require_string(name, "repository", skill.get("repository"))
        ref = require_string(name, "ref", skill.get("ref"))
        target_path = require_string(
            name,
            "target_path",
            skill.get("target_path", name),
        )
        source_path = require_string(
            name,
            "source_path",
            skill.get("source_path", "."),
        )

        validate_path(name, "target_path", target_path, allow_dot=False)
        validate_path(name, "source_path", source_path, allow_dot=True)

        if target_path in seen_target_paths:
            raise ValueError(f"duplicate target_path: {target_path}")

        seen_target_paths.add(target_path)
        records.append(
            {
                "name": name,
                "target_path": target_path,
                "repository": repository,
                "ref": ref,
                "source_path": source_path,
            }
        )

    return records


def select_upstreams(
    records: list[dict[str, str]],
    selected: str,
) -> list[dict[str, str]]:
    if selected == "all":
        return records

    matches = [record for record in records if record["name"] == selected]
    if not matches:
        raise ValueError(f"unknown third-party skill: {selected}")
    return matches


def serialize(record: dict[str, str]) -> str:
    fields = ("name", "target_path", "repository", "ref", "source_path")
    return "\t".join(record[field] for field in fields)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="path to upstreams.json")
    parser.add_argument("selection", nargs="?", default="all")
    args = parser.parse_args()

    try:
        records = select_upstreams(
            load_upstreams(args.config),
            args.selection,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for record in records:
        print(serialize(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
