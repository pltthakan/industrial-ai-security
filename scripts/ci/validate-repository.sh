#!/usr/bin/env bash

set -euo pipefail

required_files=(
  AGENTS.md
  README.md
  docs/architecture.md
  docs/project-state.md
  docs/ci-cd.md
  .github/workflows/ci.yml
)

failed=false

for path in "${required_files[@]}"; do
  if [[ ! -s "$path" ]]; then
    echo "Required file is missing or empty: $path" >&2
    failed=true
  fi
done

tracked_videos="$(git ls-files 'samples/*.mp4')"
if [[ -n "$tracked_videos" ]]; then
  echo "Sample MP4 files must not be committed to Git:" >&2
  echo "$tracked_videos" >&2
  failed=true
fi

if [[ "$failed" == true ]]; then
  exit 1
fi

echo "Repository structure is valid."

