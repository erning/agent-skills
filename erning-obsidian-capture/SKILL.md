---
name: erning-obsidian-capture
description: >-
  Save conversations, summaries, or supplied content to Erning's personal
  Obsidian Notes vault when the user explicitly targets that vault or the
  current conversation has already established it as the capture destination.
  Generic summaries, ambiguous requests to record something, and other vaults
  or project documents are outside this skill's scope.
---

# Erning Obsidian Capture

Capture the requested material as a readable Markdown note in Erning's
personal Notes repository. These defaults belong to this specific vault.

## Invocation and authorization

- An explicit capture request using `$erning-obsidian-capture`, or a request
  such as "把这个总结记到我的 Obsidian Notes", establishes the destination.
- Once this conversation establishes Notes as the capture destination,
  follow-ups such as "这个也记一下" can reuse it. A later explicit destination
  takes precedence; never redirect a README, changelog, or another vault's
  note into Notes.
- Without that context, "记录一下" does not authorize saving here. A request
  only to summarize, such as "总结一下", does not authorize a write even after
  Notes has been selected. Discussing or developing this skill is not itself
  a capture request.
- A request to save authorizes creating the date directory and writing the
  note. Do not require a routine preview or repeat an existing approval.
  Honor requests to preview first, and ask only when the content scope or
  destination remains materially ambiguous.

## Locate the vault

Personal defaults:

| Setting | Value |
| --- | --- |
| Repository | `erning/Obsidian-Notes` on GitHub |
| SSH URL | `git@github.com:erning/Obsidian-Notes.git` |
| Default checkout | `~/Projects/Obsidian/Notes` |
| Alternate checkout | `~/projects/Obsidian/Notes` |
| New notes | `Daily/YYYY-MM-DD/<note>.md` |
| Default date timezone | `Asia/Shanghai` |

Use an explicitly selected checkout first. Otherwise use
`~/Projects/Obsidian/Notes` if it exists; only check
`~/projects/Obsidian/Notes` when the capitalized path is absent. Expand `~` for
the current user and stop searching once a path is selected.

Verify that the candidate is the Git repository root and that its `origin`
identifies `github.com/erning/Obsidian-Notes`; equivalent SSH URL spellings
are valid. A directory called `Notes`, or a subdirectory inside another Git
repository, is insufficient. Do not change remotes to make a candidate fit.
If the selected path fails this check, explain the mismatch before
writing instead of falling back to another checkout.

Read applicable `AGENTS.md` instructions, including those in the vault and
the destination's ancestors. Inspect only relevant nearby notes for local
conventions or an intended update; do not scan the entire private vault to
prepare a capture.

If no matching checkout exists, prepare the requested content and ask for its
location. Clone only when the user requests initialization, using the SSH URL
above and the selected destination. Ordinary captures need no remote access.
Use the current agent's filesystem and Git capabilities; no Obsidian plugin,
application UI, or agent-specific conversation database is required.

## Select the date and note

- For a new note, use the date of recording in `Asia/Shanghai`, obtained at
  execution time, for example with `TZ=Asia/Shanghai date +%F`. Honor an
  explicit date or timezone. A historical date mentioned in the content does
  not change the destination unless the user asks to file it under that date.
- Create one focused note per requested topic. Use a short descriptive
  English filename with lowercase words separated by hyphens by default,
  preserving useful technical names. The directory already carries the date.
  Honor an explicitly requested filename, including Chinese names or spaces.
- Keep generated filenames to a single basename with a `.md` extension and
  verify that the resolved destination remains inside the selected vault.
  Use `Daily/YYYY-MM-DD/` for new notes unless the user explicitly selects
  another location within this vault.
- Read an existing destination before deciding how to proceed. An explicit
  request to continue or update a note targets that note, including on a
  previous day; preserve its path and unrelated content. A new, independent
  capture with a colliding name needs a more specific name or numeric suffix.
  A matching filename alone does not authorize replacing the existing note.
- After an interrupted or uncertain write, inspect the destination first.
  If the requested content is already present, verify and report it rather
  than creating a duplicate or appending the same material again.

Example default destination:

```text
Daily/2026-09-09/obsidian-capture-design.md
```

## Compose the content

Use the material the user selected, or the relevant part of the current
conversation. Preserve supplied or approved summaries with only the changes
needed to make them stand alone. Match the form to the request:

- **Save a summary:** retain its substantive content and established wording.
- **Record a discussion:** explain the background, key questions, conclusions
  and their reasons, and unresolved points when present.
- **Record troubleshooting:** retain the symptoms, meaningful attempts,
  observations, diagnosis, actions, and actual verification results.
- **Save a transcript:** reproduce only user-visible messages actually
  available through the current context or the target agent's supported
  retrieval tools. State any missing range; do not reconstruct unavailable
  messages as quotations.

Make references such as "the option above" understandable outside the chat.
Distinguish proposals, decisions, and completed work. Preserve uncertainty,
useful commands, configuration blocks, and supplied source links. Capturing
does not by itself request new research or unsupported factual additions.

Default to Simplified Chinese prose with technical names preserved, one
first-level title, and sections suited to the content. Follow explicit
language choices and preserve an existing note's structure when updating it.
Keep each Chinese prose paragraph on one source line. Tags are optional;
there is no required YAML frontmatter, fixed tag set, or universal outline.

Use Obsidian `[[wikilinks]]` for relevant existing notes whose targets have
been verified. Include an existing, available conversation link when useful
for provenance; do not invent a link or create a share link just to cite the
conversation. Store commands and code as fenced Markdown blocks, consistent
with this vault's documentation-only convention.

## Write and verify

Write within the selected scope and preserve unrelated edits, notes, and
vault configuration. Before updating an existing note, recheck its current
content so another writer's changes are not silently lost. A dirty working
tree does not prevent saving a note.

The default operation is a local Markdown write. Do not automatically pull,
stage, commit, or push. Execute Git operations when requested or already
authorized, using the Notes checkout as the working directory and preserving
unrelated worktree and index changes. If a requested Git operation fails,
report the saved note and the unfinished operation separately.

Read back the resulting file to verify its path, requested content, and
Markdown structure. Check the scoped diff or new file for unintended changes.
Report a clickable absolute file path and whether the note was created,
updated, or already present. Distinguish local saving from any verified Git
operations, and do not claim success when the write was not completed.
