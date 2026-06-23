#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${CODEX_HOME:-$HOME/.codex}/skills"

dry_run=0
list_only=0

usage() {
  cat <<'EOF'
Usage: ./install.sh [--dry-run] [--list]

Installs each repository directory containing SKILL.md into:
  ${CODEX_HOME:-$HOME/.codex}/skills

Options:
  --dry-run  Show what would be installed without writing files.
  --list     List skill directories found in this repository.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      dry_run=1
      ;;
    --list)
      list_only=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

find_skills() {
  for skill_md in "$ROOT"/*/SKILL.md; do
    [ -f "$skill_md" ] || continue
    dirname "$skill_md"
  done
}

skills="$(find_skills)"

if [ -z "$skills" ]; then
  echo "No skill directories found under $ROOT" >&2
  exit 1
fi

if [ "$list_only" -eq 1 ]; then
  printf '%s\n' "$skills" | while IFS= read -r skill_dir; do
    basename "$skill_dir"
  done
  exit 0
fi

if [ "$dry_run" -eq 0 ]; then
  mkdir -p "$DEST"
fi

printf '%s\n' "$skills" | while IFS= read -r skill_dir; do
  name="$(basename "$skill_dir")"
  target="$DEST/$name"

  if [ "$dry_run" -eq 1 ]; then
    echo "Would install $name -> $target"
    continue
  fi

  rm -rf "$target"
  cp -a "$skill_dir" "$target"
  echo "Installed $name -> $target"
done

echo "Restart Codex to pick up new skills."
