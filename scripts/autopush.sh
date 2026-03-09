#!/usr/bin/env bash
set -u

# Autopush script: watches repo and auto-commits & pushes changes.
# - Uses fswatch if available (macOS). Falls back to polling every 5s.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT" || exit 1
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
commit_msg_prefix="autosave"

_do_commit_push() {
  if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "${commit_msg_prefix}: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" || return
    git push origin "$branch" || return
  fi
}

if command -v fswatch >/dev/null 2>&1; then
  echo "Using fswatch to monitor changes..."
  while fswatch -1 -r .; do
    _do_commit_push
  done
else
  echo "fswatch not found, falling back to polling every 5s"
  while true; do
    _do_commit_push
    sleep 5
  done
fi
