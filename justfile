set shell := ["bash", "-euo", "pipefail", "-c"]

# Show available recipes.
default:
    @just --list

# List configured third-party skills.
list:
    @./scripts/sync-upstream-skills.sh --list

# Import or update all third-party skills, or one skill by name.
sync skill="all":
    ./scripts/sync-upstream-skills.sh "{{ skill }}"
