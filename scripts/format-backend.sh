#!/usr/bin/env bash
set -euo pipefail

# Only consider staged .py files under backend/
files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^backend/.*\.py$' || true)
[ -z "$files" ] && exit 0

cd backend
uv venv --allow-existing --quiet
source .venv/bin/activate
uv sync --quiet

# Strip the leading 'backend/' part for ruff
backend_files=()
while IFS= read -r f; do
  backend_files+=("${f#backend/}")
done <<< "$files"

ruff check --fix "${backend_files[@]}"
ruff format "${backend_files[@]}"

# Re-add to index using repo-root paths
root_paths=()
for f in "${backend_files[@]}"; do
  root_paths+=("backend/$f")
done

cd ..
git add "${root_paths[@]}"


