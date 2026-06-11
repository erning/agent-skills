#!/usr/bin/env python3
"""Test upstream skill configuration parsing."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "read-upstreams.py"
SPEC = importlib.util.spec_from_file_location("read_upstreams", SCRIPT)
assert SPEC and SPEC.loader
UPSTREAMS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(UPSTREAMS)


class UpstreamConfigTests(unittest.TestCase):
    def load(self, config: object) -> list[dict[str, str]]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "upstreams.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            return UPSTREAMS.load_upstreams(path)

    def test_defaults_paths_from_name_and_repository_root(self) -> None:
        records = self.load(
            {
                "example": {
                    "repository": "https://example.com/repo.git",
                    "ref": "main",
                }
            }
        )

        self.assertEqual(records[0]["target_path"], "example")
        self.assertEqual(records[0]["source_path"], ".")

    def test_preserves_explicit_source_and_target_paths(self) -> None:
        records = self.load(
            {
                "example": {
                    "target_path": "vendor/Example",
                    "repository": "https://example.com/repo.git",
                    "ref": "v1",
                    "source_path": "skills/example",
                }
            }
        )

        self.assertEqual(records[0]["target_path"], "vendor/Example")
        self.assertEqual(records[0]["source_path"], "skills/example")

    def test_rejects_duplicate_target_paths(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate target_path"):
            self.load(
                {
                    "first": {
                        "target_path": "shared",
                        "repository": "https://example.com/first.git",
                        "ref": "main",
                    },
                    "second": {
                        "target_path": "shared",
                        "repository": "https://example.com/second.git",
                        "ref": "main",
                    },
                }
            )

    def test_rejects_unknown_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown fields: prefix"):
            self.load(
                {
                    "example": {
                        "prefix": "example",
                        "repository": "https://example.com/repo.git",
                        "ref": "main",
                    }
                }
            )

    def test_selects_one_skill(self) -> None:
        records = self.load(
            {
                "first": {
                    "repository": "https://example.com/first.git",
                    "ref": "main",
                },
                "second": {
                    "repository": "https://example.com/second.git",
                    "ref": "main",
                },
            }
        )

        selected = UPSTREAMS.select_upstreams(records, "second")

        self.assertEqual([record["name"] for record in selected], ["second"])

    def test_rejects_unknown_selection(self) -> None:
        records = self.load(
            {
                "example": {
                    "repository": "https://example.com/repo.git",
                    "ref": "main",
                }
            }
        )

        with self.assertRaisesRegex(ValueError, "unknown third-party skill"):
            UPSTREAMS.select_upstreams(records, "missing")


if __name__ == "__main__":
    unittest.main()
