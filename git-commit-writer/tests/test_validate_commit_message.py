#!/usr/bin/env python3
"""Test commit message line-length boundaries."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_commit_message.py"
SPEC = importlib.util.spec_from_file_location("validate_commit_message", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def message_with_body_length(length: int) -> str:
    subject = "docs(readme): explain installation"
    return f"{subject}\n\n{'x' * length}\n"


class LineLengthTests(unittest.TestCase):
    def test_preferred_length_has_no_warning(self) -> None:
        message = message_with_body_length(78)

        self.assertEqual(VALIDATOR.validate(message), [])
        self.assertEqual(VALIDATOR.warnings(message), [])

    def test_lengths_up_to_maximum_only_warn(self) -> None:
        for length in (79, 80):
            with self.subTest(length=length):
                message = message_with_body_length(length)

                self.assertEqual(VALIDATOR.validate(message), [])
                self.assertEqual(len(VALIDATOR.warnings(message)), 1)

    def test_length_above_maximum_fails(self) -> None:
        message = message_with_body_length(81)

        self.assertTrue(
            any("maximum is 80" in error for error in VALIDATOR.validate(message))
        )
        self.assertEqual(VALIDATOR.warnings(message), [])


if __name__ == "__main__":
    unittest.main()
