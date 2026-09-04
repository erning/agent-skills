# AGENTS.md

This file guides coding agents maintaining this repository. See [README.md](README.md)
for the skill catalog, installation instructions, and user examples.

## Overview

A personal collection of agent skills. The main deliverables are instructions in
`SKILL.md`, with optional scripts, references, metadata, and evaluation cases.
There is no repository-wide application or build step.

## Repository Map

| Path | Purpose |
| --- | --- |
| `<skill-name>/` | Canonical source for each skill |
| `.agents/skills/`, `.claude/skills/` | Relative symlinks to selected skills used while maintaining this repository |
| `AGENTS.md` | Repository maintenance instructions |
| `CLAUDE.md` | Symlink to `AGENTS.md`; keep it as a symlink |
| `README.md` | User-facing documentation, written in Simplified Chinese |
| `upstreams.json` | Sources and destination paths for vendored third-party skills |
| `scripts/` | Upstream configuration parser and subtree sync script |
| `tests/` | Tests for repository maintenance scripts |
| `justfile` | `list` and `sync` recipes; bare `just` lists recipes |

Edit skills in their top-level source directories. Keep entries in the discovery
directories as relative symlinks rather than creating duplicate copies. These
directories expose a selection of skills; add links when a skill is needed for
repository maintenance.
Read any nested `AGENTS.md` before editing that subtree; `humanizer/` has its own
package rules.

## Skill Structure

```text
skill-name/
├── SKILL.md                 # Required: YAML name and description, then instructions
├── agents/openai.yaml       # Optional: display metadata and default prompt
├── scripts/                 # Optional: executable helpers
├── references/              # Optional: detailed material loaded on demand
├── tests/                   # Optional: tests for bundled scripts
└── evals/
    ├── evals.json           # Optional: task prompts and expected behavior
    └── trigger-evals.json   # Optional: positive and negative trigger cases
```

## Editing Skills and Documentation

- New skill directories and frontmatter names use lowercase with hyphens, such as
  `git-crypt`. Preserve the vendored `Humanizer-zh/` directory; its frontmatter
  name and installation selector are `humanizer-zh`.
- Treat `SKILL.md` as the source of truth for a skill's behavior. Keep related
  examples, references, evaluation cases, and `agents/openai.yaml` consistent
  when changing that behavior.
- Make frontmatter descriptions specific and proactive: state the task and
  trigger contexts early, and include exclusions where nearby tasks should not
  activate the skill. Avoid broad keyword matches that exceed the skill's scope.
- Keep core instructions in `SKILL.md`; put detailed reference material in
  `references/` and say when to read it.
- When a skill invokes bundled scripts, assets, or references, write paths as
  relative to that skill directory, not relative to the user's target project.
  Skills must remain usable when installed individually.
- Use the target agent's actual tools and capabilities. Do not assume tools or
  storage formats from one agent are available in another.
- Update the README catalog when adding, removing, or changing a skill's purpose.
  Use the frontmatter `name` as the installation name and link to the actual
  source path, preserving its case.
- Use `$chinese-doc-style` when creating or directly editing formal Chinese
  documentation. Preserve the existing language of other files.

## Validation

Run commands from the repository root. Choose checks that cover the changed
files; documentation-only changes need link, path, command, and diff checks,
not unrelated test suites.

| Changed area | Relevant checks |
| --- | --- |
| Upstream parser or configuration | `python3 -B -m unittest discover -s tests -v` and `python3 scripts/read-upstreams.py upstreams.json` |
| Sync shell script | `bash -n scripts/sync-upstream-skills.sh` and `./scripts/sync-upstream-skills.sh --list` |
| Commit message validator | `python3 -B -m unittest discover -s git-commit-writer/tests -v` |
| Skill discovery or frontmatter | `npx skills add . --list` (lists skills without installing; may require network access for the CLI) |
| Vendored `humanizer` package | Follow `humanizer/AGENTS.md`; its local package check is `python3 humanizer/scripts/validate-package.py` |

The Python checks use the standard library. `just` is an optional command wrapper;
the scripts can also run directly.

Evaluation JSON files describe prompts and expected outcomes; they are not run
by `unittest`, and this repository has no shared evaluation runner. When changing
skill behavior, update relevant cases and check representative prompts if an
evaluation environment is available. Report which checks actually ran.

- `evals/evals.json` uses `skill_name` and an `evals` array. Follow nearby cases
  for `id`, `prompt`, `expected_output`, `files`, and `assertions`.
- Assertions use `type: "contains"` for literal checks and `type: "semantic"`
  for meaning-based checks.
- `evals/trigger-evals.json`, where present, is an array of `query` and
  `should_trigger` pairs. Cover both intended triggers and nearby exclusions.

Before handing off, run `git diff --check` and inspect `git status --short` for
unintended files. Keep evaluation workspaces in ignored `*-workspace/` directories.

## Third-Party Skills

`upstreams.json` is the source of truth for upstream sync. Currently it maps
`humanizer` to `humanizer/` and `humanizer-zh` to `Humanizer-zh/`. These directories
are squashed Git subtrees, not submodules. Preserve their upstream metadata,
licenses, and directory names.

For an upstream update, use `just sync <name>` or
`./scripts/sync-upstream-skills.sh <name>` rather than copying files manually.
Use `just list` or the script's `--list` option to inspect configured names.
See the README for the configuration fields and first-import workflow.

Sync requires Bash, Python 3, Git with `git subtree`, upstream access, and a clean
working tree, including no untracked files. It fetches content and creates Git
commits, so it is a maintenance operation, not a validation command. Keep local
edits to vendored skills focused and distinguish them from upstream sync changes.

## Commits

Use `$git-commit-writer` when creating, checking, or amending commit messages.
Messages use English ASCII Conventional Commits with a non-empty scope and a
useful body. Use the skill name as the scope for skill changes; for shared files,
choose a scope that identifies the affected area. Follow the skill for the full
format and validation rules.
