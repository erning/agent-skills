---
name: git-commit-writer
description: >-
  Write or check Git commit messages using Erning's conventions. Use whenever
  the user asks to commit changes, draft or validate a commit message, amend a
  commit message, or prepare a Conventional Commit. Enforce an English ASCII
  Conventional Commit subject, a required useful body with restrained line
  width, and no authorship or AI-generation attribution.
---

# Git Commit Message Conventions

Apply this skill only to the commit message. Do not add repository inspection,
diff review, staging, permission, or commit-execution steps solely because this
skill is active; follow the surrounding task instructions for those operations.

Use this structure:

```text
type(scope): imperative description

Explain what changed and why it was needed.
```

Follow these rules:

- Use one of `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`,
  `revert`, `style`, or `test`.
- Require a non-empty lowercase scope containing only ASCII letters, digits,
  `.`, `_`, or `-`.
- Add `!` before `:` only for a breaking change.
- Write a concise imperative subject and do not end it with a period.
- Separate the subject and body with exactly one blank line.
- Always include a useful body that explains the reason, effect, or important
  implementation detail without merely repeating the subject.
- Write the entire message in English ASCII.
- Keep body lines at 78 characters or fewer when possible and never exceed
  80 characters.
- Do not add authorship, AI-generation, tool, model, vendor, or equivalent
  attribution.
- Describe only facts supported by the changes. Do not invent issue numbers or
  context.

Run the bundled `scripts/validate_commit_message.py` only when the user
explicitly asks to validate a proposed message. Do not run it for ordinary
commit requests.
