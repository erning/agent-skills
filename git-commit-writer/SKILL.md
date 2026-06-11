---
name: git-commit-writer
description: >-
  Create Git commits using Erning's personal commit conventions. Inspect
  repository instructions, git status, staged changes, diffs, and recent
  commits; stage only relevant files; write validated English ASCII
  Conventional Commit messages with useful bodies and no attribution. Use
  whenever the user asks to commit changes, "commit this", draft or check a
  commit message, amend a commit message, or prepare a conventional commit.
---

# Git Commit Writer

Create self-contained Git commit messages without automated attribution.

## Workflow

1. Read repository instructions before preparing the commit.
2. Inspect `git status --short`, the staged diff, and recent commits.
3. Stage only files that belong to the requested change.
   Do not include unrelated user changes.
4. Choose a Conventional Commits type and a concise, meaningful scope.
5. Write the message to a temporary file.
6. Resolve the validator from this skill directory and run
   `<skill-dir>/scripts/validate_commit_message.py <message-file>`.
7. Fix every reported error before committing.
8. Commit with `git commit -F <message-file>`.
9. Report the commit hash and subject.

Do not commit when no relevant changes exist. Do not amend, force, or bypass
hooks unless the user explicitly requests it.

## Message Format

Use this structure:

```text
type(scope): imperative description

Explain what changed and why it was needed. Include important implementation
details, behavioral effects, constraints, or follow-up considerations.
```

Apply all of these rules:

- Write the subject as `type(scope): description`.
- Require a non-empty lowercase scope using ASCII letters, digits, `.`, `_`,
  or `-`.
- Use one of: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`,
  `refactor`, `revert`, `style`, or `test`.
- Add `!` before `:` only for a breaking change.
- Use imperative mood in the subject, such as `add`, `fix`, or `remove`.
- Keep the subject concise and do not end it with a period.
- Separate the subject and body with exactly one blank line.
- Always write a useful body. Do not merely repeat the subject.
- Aim to wrap every non-empty line at 78 characters or fewer.
  Never exceed 80 characters.
- Use English and ASCII characters only.
- Describe facts visible from the change.
  Do not invent issue numbers or context.

## Attribution

Do not add authorship or AI-generation attribution to a commit message.

Forbidden content includes:

```text
Co-Authored-By: ...
Co-authored-by: ...
Generated-By: ...
Generated-With: ...
```

Do not add equivalent prose, tool names, model names, or vendor attribution.

## Examples

```text
feat(parser): add support for nested configuration blocks

Parse nested blocks recursively and preserve source locations. This lets
callers report validation errors against the original configuration lines.
```

```text
fix(auth): reject expired refresh tokens before rotation

Check token expiration before issuing a replacement token. This prevents
expired sessions from being extended through the refresh endpoint.
```

## Validation Script

The validator is bundled with this skill. Resolve `scripts/` relative to the
directory containing this `SKILL.md`, not relative to the target repository.
When your shell is in the target repository, use the script's absolute path.

Run:

```bash
python3 <skill-dir>/scripts/validate_commit_message.py /path/to/message.txt
```

Pass `-` to read from standard input. The script checks structure, types,
required body, ASCII text, line length, and forbidden attribution. Lines with
79 or 80 characters produce warnings; lines longer than 80 characters fail.
