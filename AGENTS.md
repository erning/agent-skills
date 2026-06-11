# AGENTS.md

This file provides guidance to coding agents working in this repository.

## Overview

A personal collection of agent skills. Each skill is a self-contained top-level directory with a `SKILL.md` and optional supporting files.

## Skill Structure

```
skill-name/
├── SKILL.md              # Required. YAML frontmatter (name, description) + markdown instructions
├── references/            # Optional. Deep-dive docs, loaded on demand
└── evals/evals.json       # Optional. Test cases for evaluating skill quality
```

## Conventions

- Skill directories use lowercase with hyphens: `git-crypt`, `macos-input-method`
- Git commits follow Conventional Commits: `feat(skill-name): description`
- Use `$git-commit-writer` when creating, checking, or amending commits.
- Skill descriptions in frontmatter should be "pushy" — include trigger contexts so the agent invokes the skill when relevant
- When a skill invokes bundled scripts, assets, or references, write paths as
  relative to that skill directory, not relative to the user's target project.
- `evals.json` assertions use `type: "contains"` for literal checks and `type: "semantic"` for meaning-based checks
