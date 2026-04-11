# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A personal collection of Claude Code skills. Each skill is a self-contained top-level directory with a `SKILL.md` and optional supporting files.

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
- Skill descriptions in frontmatter should be "pushy" — include trigger contexts so Claude invokes the skill when relevant
- `evals.json` assertions use `type: "contains"` for literal checks and `type: "semantic"` for meaning-based checks
