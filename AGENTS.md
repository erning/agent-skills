# AGENTS.md

This file guides coding agents maintaining this repository. See
[README.md](README.md) for the skill catalog, installation instructions, and
user examples.

## Source and scope

This repository develops skills; user-level skill directories contain
installed copies. Work in the top-level source directories. Installation and
changes to user-level copies are separate tasks.

Keep `.agents/skills/` and `.claude/skills/` entries as relative symlinks to
the selected source skills. Keep `CLAUDE.md` as a symlink to `AGENTS.md`. Read
nested `AGENTS.md` files when working in their subtree; `humanizer/` has
package-specific rules. There is no repository-wide build step.

## Editing Skills and Documentation

- New skill directories and frontmatter names use lowercase with hyphens, such
  as `git-crypt`. Preserve the vendored `Humanizer-zh/` directory; its
  frontmatter name and installation selector are `humanizer-zh`.
- Treat `SKILL.md` as the source of truth for a skill's behavior. Keep related
  examples, references, evaluation cases, and `agents/openai.yaml` consistent
  when changing that behavior.
- Keep descriptions short and task-specific. Put the main use case first and
  include exclusions only for likely confusion; avoid keyword catchalls.
- Include guidance that changes decisions: local conventions, non-obvious
  constraints, and completion criteria. Avoid generic recipes and repeated
  rules.
- Keep shared instructions in `SKILL.md`. Route substantial task-specific
  detail to `references/` with conditions for reading it; small skills can
  stay in one file.
- Preserve explicit user choices and existing authorization. Require another
  confirmation only when an unresolved decision or new scope needs it.
- When a skill invokes bundled scripts, assets, or references, write paths as
  relative to that skill directory, not relative to the user's target project.
  Skills must remain usable when installed individually.
- Use the target agent's actual tools and capabilities. Do not assume tools or
  storage formats from one agent are available in another.
- Update the README catalog when adding, removing, or changing a skill's
  purpose. Use the frontmatter `name` as the installation name and link to the
  actual source path, preserving its case.
- Use `$chinese-doc-style` when creating or directly editing formal Chinese
  documentation, or specifically reviewing its typography and formatting.
  Reading, summarizing, or reviewing facts and logic alone does not trigger
  it. Preserve the existing language of other files.
- Keep each Chinese prose paragraph, including paragraphs within list items,
  on one source line; use editor soft wrapping instead of a fixed column
  width. Preserve structural line breaks, literal blocks, and intentional line
  breaks.
- English document prose may use hard wrapping. Keep lines at 78 characters or
  fewer when possible and never exceed 80 characters. Do not leave trailing
  whitespace. Preserve code, tables, URLs, and other indivisible Markdown
  units when wrapping would change their content or structure. Commit messages
  follow the strict subject and body limits in `$git-commit-writer`.

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

The Python checks use the standard library. `just` is an optional command
wrapper; the scripts can also run directly.

Evaluation JSON files describe prompts and expected outcomes; they are not run
by `unittest`, and this repository has no shared evaluation runner. When
changing skill behavior, update relevant cases and check representative
prompts if an evaluation environment is available. Report which checks
actually ran.

- `evals/evals.json` uses `skill_name` and an `evals` array. Follow nearby
  cases for `id`, `prompt`, `expected_output`, `files`, and `assertions`.
- Assertions use `type: "contains"` for literal checks and `type: "semantic"`
  for meaning-based checks.
- `evals/trigger-evals.json`, where present, is an array of `query` and
  `should_trigger` pairs. Cover both intended triggers and nearby exclusions.

Before handing off, run `git diff --check` and inspect `git status --short`
for unintended files. Keep evaluation workspaces in ignored `*-workspace/`
directories.

## Third-Party Skills

`upstreams.json` is the source of truth for upstream sync. Currently it maps
`humanizer` to `humanizer/` and `humanizer-zh` to `Humanizer-zh/`. These
directories are squashed Git subtrees, not submodules. Preserve their upstream
metadata, licenses, and directory names.

Keep `humanizer/` identical to the imported upstream version unless a concrete
usage problem requires a local fix. Preserve its upstream formatting and
validation rules; do not rewrap it to match this repository's line width.

Maintain `Humanizer-zh/` as a locally customized skill. Its user-approved
behavior and Chinese adaptations take precedence during upstream sync. Review
upstream changes and preserve these local choices when resolving conflicts.

For an upstream update, use `just sync <name>` or
`./scripts/sync-upstream-skills.sh <name>` rather than copying files manually.
Use `just list` or the script's `--list` option to inspect configured names.
See the README for the configuration fields and first-import workflow.

Sync requires Bash, Python 3, Git with `git subtree`, upstream access, and a
clean working tree, including no untracked files. It fetches content and
creates Git commits, so it is a maintenance operation, not a validation
command. Keep local edits to vendored skills focused and distinguish them from
upstream sync changes.

## Commits

Use `$git-commit-writer` when creating, checking, or amending commit messages.
Use the skill name as the scope for skill changes; for shared files, choose a
scope that identifies the affected area. Follow the skill for message format.
