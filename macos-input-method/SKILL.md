---
name: macos-input-method
description: >-
  Create, modify, install, or debug macOS input methods built with
  InputMethodKit. Use for IMKServer, input-controller, composition, and
  candidate handling within an IME; general keyboard settings or remapping
  tasks do not trigger this skill.
---

# macOS input methods

InputMethodKit input methods are macOS application bundles whose processes are
launched by the system. Preserve the target project's build tools and layout.

## Choose the relevant guidance

- Create an application or change bundle metadata and the server entry point:
  [references/project.md](references/project.md).
- Install or update a built input source:
  [references/installation.md](references/installation.md).
- Diagnose discovery, connection, controller, or event-handling failures:
  [references/troubleshooting.md](references/troubleshooting.md).
- Implement marked text, candidates, menus, lifecycle hooks, or registration:
  search the relevant section of
  [references/imkit-api.md](references/imkit-api.md).

Read only what the task needs. A candidate-window change normally does not
need project scaffolding or installation instructions.

## Shared invariants

- Use an application bundle with an identifier containing `.inputmethod.` and
  `LSBackgroundOnly` set to `true`.
- Match `InputMethodConnectionName` to the name passed to `IMKServer` and keep
  the server alive for the process lifetime.
- Match `InputMethodServerControllerClass` to the controller's Objective-C
  runtime name, commonly supplied by `@objc(...)` in Swift.
- Disable App Sandbox for the default local-development setup. When diagnosing
  connection failures, inspect sandbox settings as well as the name and
  lifetime.
- Return `true` for handled input and `false` for passthrough. Choose an event
  handling entry point appropriate to the feature; multiple overrides can
  interact.
- Reference an icon only if its asset is included in the built bundle.

Complete the requested implementation and relevant checks. Installing an input
source, selecting it, and logging the user out are separate side effects;
carry out only those authorized by the task. State whether validation used a
macOS build, an installed input source, or only source inspection.
