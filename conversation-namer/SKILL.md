---
name: conversation-namer
description: >-
  Rename and standardize conversation titles using MMDD｜TYPE｜Topic. Use when
  the user asks to rename chats or threads, organize conversation titles, or
  apply consistent sidebar naming in Codex, ChatGPT, or another conversation
  platform. Preview changes and obtain confirmation before renaming. Does not
  apply to naming projects, editing conversation content, or reviewing a naming
  prompt without a request to rename conversations.
---

# Conversation Namer

Rename conversations within the requested scope. Use the same naming rules
across platforms; adapt discovery and title updates to the capabilities actually
available in the current environment.

## Scope and capabilities

- Use the user's selected conversations or specified project, workspace, folder,
  or equivalent container. For "current project," resolve its identity from
  host context or metadata. Do not match by display name alone when ambiguous.
- By default, include non-archived conversations in that scope, including pinned
  conversations. Include archived conversations only when requested, and read
  them without restoring them. Follow explicit user scope and filters.
- If the platform has no project concept, use an explicit selection or named
  container. If the intended scope cannot be resolved, ask one concise question
  before preparing the proposal. Do not expand to the entire account.
- Use available platform tools, documented APIs or CLIs, or supported UI controls.
  Inspect their actual capabilities instead of assuming Codex tools or particular
  field names exist on every platform. Do not directly edit internal databases
  or conversation files to bypass a missing rename capability.
- Obtain a stable conversation ID or equivalent unambiguous locator, current
  title, scope membership, original creation timestamp, and enough content or a
  reliable summary to understand the topic. Follow pagination to cover the scope.
- A platform's `created_at` or similar field is acceptable only when its meaning
  is the conversation's original creation time, equivalent to `createdAt`.
- If the environment can only read conversations or supplied exports, provide
  a preview when possible and explain the missing write capability before the
  preview. Never claim that producing proposed titles renames conversations.

Change only conversation titles. Never rename a project or container, edit
conversation content, move conversations, reorder items, or change pin or archive
state. If a rename method is known to change a protected state as a side effect,
do not use it; explain the limitation. Do not perform compensating moves or
reordering operations.

## Naming rules

Use exactly:

```text
MMDD｜TYPE｜Topic
```

The separator is the fullwidth vertical line `｜` (U+FF5C), with no surrounding
spaces.

### Date

- Derive `MMDD` from the original `createdAt`, converted to `Asia/Shanghai`.
  Zero-pad the month and day. For example, `2026-09-03T17:30:00Z` becomes `0904`.
- Interpret timestamp units and the source time zone using the platform's field
  definition. Do not assume an offset for an ambiguous local timestamp.
- Never substitute `updatedAt`, last activity, export time, file timestamps, the
  current date, or a date already present in the title.
- If the original creation time cannot be established, keep the original title.

### Type

Choose the type that best describes the conversation's primary purpose or
outcome, based on its content rather than its existing title alone.

| English code | Chinese label | Use for |
| --- | --- | --- |
| FEA | 功能 | Adding a feature or capability |
| DES | 设计 | Designing behavior, architecture, interfaces, or an implementation plan |
| FIX | 修复 | Diagnosing or correcting a bug |
| OPT | 优化 | Improving existing behavior, performance, or usability |
| REL | 发布 | Preparing a release, publishing, or delivering changes |
| EXP | 探索 | Trying approaches, prototyping, or checking feasibility |
| DOC | 文档 | Writing or maintaining documentation |
| RES | 研究 | Investigating a question through sources, evidence, or comparisons |

Use English codes by default. Use the Chinese labels only when the user
explicitly requests Chinese types or Chinese titles. A Chinese user message or
Chinese conversation content alone does not change this default. Use one TYPE
language throughout the run; never mix codes and Chinese labels in new titles.

For conversations covering several activities, choose the main substantive
outcome. An incidental final action such as committing code does not make a bug
fix a release conversation. If the type remains unclear, keep the original title.

### Topic

- Summarize what the conversation is actually about, using a short, specific
  phrase suitable for a sidebar. Read more content if the available summary is
  insufficient. If the topic remains unclear, keep the original title.
- Do not repeat the project or container name. Avoid generic topics such as
  "Discussion," "Updates," or "Various fixes."
- Unless the user requests another language, follow each conversation's primary
  language for Topic. Preserve useful technical names and identifiers. Topic
  language is independent of the run's TYPE language.
- Avoid extra `｜` separators or line breaks inside Topic.
- Leave an already compliant, accurate title unchanged. When changing an existing
  structured title, replace its prefix rather than prepending another one.

These examples assume creation dates whose Shanghai month and day match the
shown prefixes. Determine the date and topic from metadata and content when
performing real work.

| Before | After |
| --- | --- |
| Improve batch text display | 0903｜OPT｜Batch text display |
| New feature discussion | 0901｜DES｜UI alignment check |
| 优化批次文字显示 | 0903｜OPT｜批次文字显示 |

When Chinese titles are explicitly requested:

| Before | After |
| --- | --- |
| 优化批次文字显示 | 0903｜优化｜批次文字显示 |
| 提交代码到 GitHub | 0813｜发布｜提交代码到GitHub |

## Preview and confirmation

Before any title mutation, prepare the complete proposal and present only a
two-column table in the preview response, with this exact header:

```markdown
| Before | After |
| --- | --- |
```

- Include the scoped conversations in their retrieved order. For skipped or
  already compliant conversations, repeat the original title in both columns.
- Preserve the actual titles in the table, escaping Markdown as needed. Do not
  add IDs, status annotations, commentary, or extra columns to the preview.
- Retain an internal mapping of each row to the conversation's stable ID,
  scope, original title, and proposed title. Do not identify rename targets by
  title or row position alone; different conversations can share a title.
- End the response after the table and wait for the user's confirmation. An
  initial request to rename is not confirmation of a proposal not yet shown.
- If the user revises the proposal, show the updated table before applying it.
  Confirmation can cover all proposed changes or an explicitly selected subset.

When there are no conversations in scope, report that result without inventing
rows. If missing access or unresolved scope prevents a meaningful preview, state
the specific limitation or ask for the missing information instead of guessing.

## Apply and report

After confirmation, update only the approved titles that differ from the
originals. Use the retained IDs or locators and recheck the current title and
scope before each update. If either has changed since the preview, skip that
conversation and report the conflict. Newly discovered conversations require a
new proposal and are not covered by the earlier confirmation.

Use a title-specific update operation. If an operation times out or has an
uncertain result, read the current title before retrying; if it already equals
the approved title, do not write again. Verify the resulting titles through a
readback or an authoritative update response. Stop retrying when success cannot
be established or the operation would exceed the approved scope.

After the rename attempt, report only results: successful renames, unchanged or
skipped items, and failures with concise reasons. A compact results table is
appropriate. Do not claim unverified changes succeeded or append unrelated
advice, follow-up offers, or project-management actions.
