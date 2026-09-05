#!/usr/bin/env python3
"""Test commit message format, attribution boundaries, and CLI behavior."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
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


def message_with_subject_length(length: int) -> str:
    prefix = "docs(readme): "
    subject = prefix + "x" * (length - len(prefix))
    return f"{subject}\n\nExplain how to install the skill.\n"


class LineLengthTests(unittest.TestCase):
    def test_preferred_length_has_no_warning(self) -> None:
        for make_message in (message_with_body_length, message_with_subject_length):
            with self.subTest(area=make_message.__name__):
                message = make_message(78)
                self.assertEqual(VALIDATOR.validate(message), [])
                self.assertEqual(VALIDATOR.warnings(message), [])

    def test_lengths_up_to_maximum_only_warn(self) -> None:
        for make_message in (message_with_body_length, message_with_subject_length):
            for length in (79, 80):
                with self.subTest(area=make_message.__name__, length=length):
                    message = make_message(length)
                    self.assertEqual(VALIDATOR.validate(message), [])
                    self.assertEqual(len(VALIDATOR.warnings(message)), 1)

    def test_length_above_maximum_fails(self) -> None:
        for make_message in (message_with_body_length, message_with_subject_length):
            with self.subTest(area=make_message.__name__):
                message = make_message(81)
                self.assertTrue(any(
                    "maximum is 80" in error for error in VALIDATOR.validate(message)
                ))
                self.assertEqual(VALIDATOR.warnings(message), [])


class FormatTests(unittest.TestCase):
    def test_valid_scopes_and_breaking_marker(self) -> None:
        for subject in (
            "docs(readme): clarify installation",
            "fix(api.v2_client-core): retain optional fields",
            "feat(2fa)!: require a recovery code",
        ):
            with self.subTest(subject=subject):
                self.assertEqual(VALIDATOR.validate(f"{subject}\n\nExplain the change.\n"), [])

    def test_invalid_types_and_scopes(self) -> None:
        for subject in (
            "update(readme): clarify installation",
            "docs: clarify installation",
            "docs(): clarify installation",
            "docs(README): clarify installation",
            "docs(_internal): clarify installation",
            "docs(.internal): clarify installation",
            "docs(-internal): clarify installation",
            "docs(api/client): clarify installation",
            "docs(api client): clarify installation",
        ):
            with self.subTest(subject=subject):
                self.assertTrue(VALIDATOR.validate(f"{subject}\n\nExplain the change.\n"))

    def test_description_boundaries(self) -> None:
        for description in ("", "Clarify installation", "2 installation steps", "clarify installation."):
            with self.subTest(description=description):
                self.assertTrue(VALIDATOR.validate(
                    f"docs(readme): {description}\n\nExplain the change.\n"
                ))
        self.assertEqual(VALIDATOR.validate(
            "docs(readme): clarify GitHub installation\n\nExplain the change.\n"
        ), [])

    def test_body_and_separator_are_required(self) -> None:
        subject = "docs(readme): clarify installation"
        for message in (
            "", "\n", f"{subject}\n", f"{subject}\n\n",
            f"{subject}\nBody without separator.\n",
            f"{subject}\n\n\nBody after two blank lines.\n",
            f"{subject}\n \nBody after a space.\n",
            f"{subject}\n\n \n",
        ):
            with self.subTest(message=message):
                self.assertTrue(VALIDATOR.validate(message))

    def test_non_ascii_is_rejected_in_subject_and_body(self) -> None:
        for message in (
            "docs(readme): clarify 中文 installation\n\nExplain the change.\n",
            "docs(readme): clarify installation\n\nExplain the change — with examples.\n",
        ):
            with self.subTest(message=message):
                self.assertTrue(any(
                    "non-ASCII" in error for error in VALIDATOR.validate(message)
                ))

    def test_trailing_whitespace_is_rejected(self) -> None:
        for message in (
            "docs(readme): clarify installation \n\nExplain the change.\n",
            "docs(readme): clarify installation\n\nExplain the change.\t\n",
        ):
            with self.subTest(message=message):
                self.assertTrue(any(
                    "trailing whitespace" in error for error in VALIDATOR.validate(message)
                ))

    def test_crlf_and_multiple_body_paragraphs(self) -> None:
        message = (
            "docs(readme): clarify installation\r\n\r\n"
            "Separate local and global installation examples.\r\n\r\n"
            "Explain where each command installs the skill.\r\n"
        )
        self.assertEqual(VALIDATOR.validate(message), [])


class AttributionTests(unittest.TestCase):
    def test_common_attribution_lines_are_rejected(self) -> None:
        for attribution in (
            "Co-authored-by: Example <author@example.com>",
            "Authored-by: Example <author@example.com>",
            "Signed-off-by: Example <author@example.com>",
            "Generated-by: Codex",
            "Generated-with: Claude Code",
            "Generated by ChatGPT.",
            "GENERATED BY CHATGPT.",
            "Generated with Claude Code",
            "Written using OpenAI.",
            "Generated with [Claude Code](https://claude.com/claude-code)",
            "This commit message was generated by a local assistant.",
            "Codex generated this commit.",
            "AI-generated commit message",
        ):
            with self.subTest(attribution=attribution):
                message = f"docs(readme): clarify installation\n\nExplain the change.\n\n{attribution}\n"
                errors = VALIDATOR.validate(message)
                self.assertTrue(any("forbidden attribution" in error for error in errors))

    def test_tool_names_and_metadata_in_change_prose_are_allowed(self) -> None:
        messages = (
            "fix(parser): preserve generated-by metadata\n\nRetain this field in document headers.\n",
            "fix(codex): retain generated fixtures\n\nKeep Codex-generated fixtures for reproducible builds.\n",
            "fix(parser): retain metadata\n\nGenerated-by metadata is preserved during parsing.\n",
            "docs(codex): describe fixture storage\n\nCodex generated fixtures that the tests now reuse.\n",
            "docs(api): explain provider selection\n\nDocument how to select OpenAI or Anthropic as the provider.\n",
            "fix(parser): retain attribution fields\n\nPreserve the Co-authored-by field when parsing existing records.\n",
        )
        for message in messages:
            with self.subTest(message=message):
                self.assertEqual(VALIDATOR.validate(message), [])


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str, message: str = "") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *args], input=message,
            capture_output=True, text=True, check=False,
        )

    def test_valid_stdin_reports_only_mechanical_success(self) -> None:
        result = self.run_cli("-", message=message_with_body_length(78))
        self.assertEqual(result.returncode, 0)
        self.assertIn("passes mechanical checks", result.stdout)
        self.assertIn("content review is still needed", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_stdin_warning_keeps_success_exit_code(self) -> None:
        result = self.run_cli("-", message=message_with_body_length(80))
        self.assertEqual(result.returncode, 0)
        self.assertIn("warning:", result.stderr)

    def test_invalid_message_has_error_exit_code(self) -> None:
        result = self.run_cli("-", message="docs(readme): clarify installation\n")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("non-empty body", result.stderr)

    def test_file_input_and_read_errors(self) -> None:
        with tempfile.TemporaryDirectory(suffix="-workspace") as directory:
            path = Path(directory) / "message.txt"
            path.write_text(message_with_body_length(78), encoding="utf-8")
            self.assertEqual(self.run_cli(str(path)).returncode, 0)
            path.write_bytes(b"\xff")
            invalid_encoding = self.run_cli(str(path))
            self.assertEqual(invalid_encoding.returncode, 2)
            self.assertIn("cannot read commit message", invalid_encoding.stderr)
            missing = self.run_cli(str(path.with_name("missing.txt")))
            self.assertEqual(missing.returncode, 2)
            self.assertIn("cannot read commit message", missing.stderr)


if __name__ == "__main__":
    unittest.main()
