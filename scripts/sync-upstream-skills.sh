#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR=$(git rev-parse --show-toplevel)
CONFIG_FILE=${UPSTREAMS_CONFIG:-"$ROOT_DIR/upstreams.json"}
cd "$ROOT_DIR"

read_upstreams() {
  python3 scripts/read-upstreams.py "$CONFIG_FILE" "${1:-all}"
}

validate_message() {
  printf '%s\n' "$1" |
    python3 git-commit-writer/scripts/validate_commit_message.py - >/dev/null
}

sync_skill() {
  local name=$1
  local target_path=$2
  local repository=$3
  local ref=$4
  local source_path=$5
  local body
  local message
  local split_commit
  local subject

  if [[ "$source_path" != "." ]]; then
    printf 'Fetching %s from %s (%s)...\n' "$name" "$repository" "$ref"
    git fetch --quiet "$repository" "$ref"
    split_commit=$(
      git subtree split \
        --prefix="$source_path" \
        FETCH_HEAD
    )
  fi

  if [[ -e "$target_path" ]]; then
    printf 'Syncing %s from %s (%s)...\n' "$name" "$repository" "$ref"
    subject="chore($name): sync upstream skill"
    body="Sync the vendored subtree with its configured upstream source."
    printf -v message '%s\n\n%s' "$subject" "$body"
    validate_message "$message"

    if [[ "$source_path" == "." ]]; then
      git subtree pull \
        --prefix="$target_path" \
        "$repository" \
        "$ref" \
        --squash \
        --message="$message"
    else
      git subtree merge \
        --prefix="$target_path" \
        "$split_commit" \
        --squash \
        --message="$message"
    fi
  else
    printf 'Importing %s from %s (%s)...\n' "$name" "$repository" "$ref"
    subject="feat($name): import upstream skill"
    body="Vendor the configured upstream source as a squashed Git subtree."
    printf -v message '%s\n\n%s' "$subject" "$body"
    validate_message "$message"

    if [[ "$source_path" == "." ]]; then
      git subtree add \
        --prefix="$target_path" \
        "$repository" \
        "$ref" \
        --squash \
        --message="$message"
    else
      git subtree add \
        --prefix="$target_path" \
        "$split_commit" \
        --squash \
        --message="$message"
    fi
  fi
}

selection=${1:-all}

if [[ "$selection" == "--help" || "$selection" == "-h" ]]; then
  echo "usage: $0 [--list|all|SKILL_NAME]"
  exit 0
fi

if [[ "$selection" == "--list" ]]; then
  records=$(read_upstreams all)
  while IFS=$'\t' read -r name _; do
    printf '%s\n' "$name"
  done <<< "$records"
  exit 0
fi

records=$(read_upstreams "$selection")

if [[ -n $(git status --porcelain) ]]; then
  echo "error: working tree must be clean before syncing subtrees" >&2
  exit 1
fi

while IFS=$'\t' read -r name target_path repository ref source_path; do
  sync_skill "$name" "$target_path" "$repository" "$ref" "$source_path"
done <<< "$records"
