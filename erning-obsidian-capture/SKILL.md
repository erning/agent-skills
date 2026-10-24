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

Save the requested material as a draft-quality Markdown note in Erning's
personal Notes repository. Keep the workflow cheap: one preparation command,
one write, no routine read-back.

## Invocation and authorization

- An explicit request such as `$erning-obsidian-capture` or "把这个总结记到我的
  Obsidian Notes" establishes the destination and authorizes writing. Do not
  ask for a routine preview or repeat an existing approval; honor a request to
  preview first.
- Once the conversation has established Notes, follow-ups such as "这个也记一下"
  reuse it. A later explicit destination wins; never redirect a README,
  changelog, or another vault's note into Notes.
- "记录一下" with no established destination, or a request only to summarize,
  does not authorize a write. Discussing this skill is not a capture request.
- Ask only when the content scope or destination is materially ambiguous.

## Locate the vault

| Setting | Value |
| --- | --- |
| Repository | `erning/Obsidian-Notes` on GitHub |
| SSH URL | `git@github.com:erning/Obsidian-Notes.git` |
| Checkout | `~/Projects/Obsidian/Notes`, else `~/projects/Obsidian/Notes` |
| New notes | `Daily/YYYY-MM-DD/<note>.md` |
| Default timezone | `Asia/Shanghai` |

Use an explicitly selected checkout first; otherwise the first default path
that exists. The lowercase path matters only on case-sensitive filesystems.

Gather everything in one command (POSIX sh; set `v` to the user's checkout
and `d` to an explicit date when given):

```sh
v=~/Projects/Obsidian/Notes; [ -d "$v" ] || v=~/projects/Obsidian/Notes
d=$(TZ=Asia/Shanghai date +%F)
git -C "$v" remote get-url origin; ls "$v/Daily/$d"; cat "$v/AGENTS.md"
```

- `origin` must identify `github.com/erning/Obsidian-Notes`; equivalent SSH
  or HTTPS spellings are valid. A directory merely named `Notes`, or a
  subdirectory of another repository, fails this check. On a mismatch, explain
  it before writing; do not change remotes or fall back to another checkout.
- Follow the vault-root `AGENTS.md` if present. Do not walk ancestor
  directories or scan other notes.
- If no checkout exists, prepare the content and ask for its location. Clone
  (SSH URL above) only when the user asks for initialization.

## Date and filename

- Use the current `Asia/Shanghai` date for a new note unless the user gives a
  date or timezone. A date mentioned in the content does not change the
  destination.
- One note per topic. Default filename: short lowercase English words joined
  by hyphens, `.md`, a single basename inside `Daily/YYYY-MM-DD/`. Honor an
  explicitly requested filename, including Chinese names or spaces.
- Use the directory listing from the preparation command to avoid collisions.
  A new, independent capture whose name collides gets a more specific name or
  numeric suffix; never overwrite or append to the existing note.
- An explicit request to continue or update a note targets that note, even
  from a previous day. Read it immediately before editing, preserve its path
  and unrelated content, and keep any changes that appeared since you last
  saw it.

## Compose the content

Write a concise draft from the user's material or the relevant part of the
conversation; full sections are not required. Make it understandable outside
the chat, with no dangling "the option above".

- **Summary:** keep the supplied or approved summary as is.
- **Discussion:** conclusions and reasons, plus open points if any.
- **Troubleshooting:** symptoms, diagnosis, fix, and the verification that
  actually happened.
- **Transcript:** only messages actually available in context or through the
  agent's real retrieval tools. State the missing range, label summaries as
  summaries, and never reconstruct unavailable messages as quotations.

Distinguish proposals, decisions, and completed work, and keep uncertainty,
useful commands, and supplied links. Do not add research or unsupported
facts, invent conversation links, or create share links.

Default to Simplified Chinese prose with technical names preserved and one
first-level title; follow explicit language choices and an updated note's
existing structure. Keep each Chinese paragraph on one source line. No
frontmatter, fixed tags, or outline is required. Put commands and code in
fenced blocks. Use `[[wikilinks]]` only for notes the user named or that you
already know exist; do not search the vault to add links.

## Write and report

Write only the note. Preserve unrelated edits and vault configuration; a
dirty working tree does not block saving. Do not pull, stage, commit, or push
unless requested or already authorized; then run Git from the checkout,
preserving unrelated worktree and index changes.

- Trust the write tool's success result for a new note: no read-back, diff,
  or echo of the content.
- Read the file back only after updating an existing note, or after an
  interrupted or uncertain write. If the requested content is already
  present, report it instead of writing again.
- Reply with the clickable absolute path and whether the note was created,
  updated, or already present. If a requested Git operation failed, report
  the saved note and the unfinished operation separately. Never claim
  success for a write that did not complete.
