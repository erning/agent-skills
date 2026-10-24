# Agent-specific rename mechanisms

Read only the section for the target agent. Agents not listed here have no
recorded mechanism; follow the general rules in `SKILL.md`.

## pi

Verified against the pi session documentation (`docs/session-format.md`,
`docs/slash-commands.md`).

- Sessions live in `~/.pi/agent/sessions/--<cwd path>--/`, one
  `<timestamp>_<id>.jsonl` file each. The directory name is the working
  directory with the leading `/` removed and `/`, `\`, `:` replaced by `-`.
- The first line is the header (`"type":"session"`) with `id`, `cwd`, and
  `timestamp`; the timestamp is the original creation time (ISO 8601, UTC).
- The display name is the last `session_info` entry in the file. Without one,
  pi shows the first message.
- Rename the current session with `/name <title>`. Extensions use
  `pi.setSessionName()`.
- To rename another session, append one `session_info` line to its file:
  `"type":"session_info"`, a fresh 8-character hex `id`, `parentId` set to
  the `id` of the last non-header entry, the current ISO `timestamp`, and
  `name` set to the new title.
- Append only; never rewrite existing lines. Skip a session that is
  currently running, because its writer may append concurrently.
