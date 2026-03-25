#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if command -v hadolint >/dev/null 2>&1; then
  hadolint "$repo_root/docker/Dockerfile"
  exit 0
fi

docker run --rm -i hadolint/hadolint < "$repo_root/docker/Dockerfile"
