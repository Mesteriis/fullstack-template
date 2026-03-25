#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sha="${GITHUB_SHA:-}"
if [[ -z "$sha" ]]; then
  sha="$(git -C "$repo_root" rev-parse HEAD 2>/dev/null || echo local)"
fi

branch="${GITHUB_REF_NAME:-}"
if [[ -z "$branch" ]]; then
  branch="$(git -C "$repo_root" rev-parse --abbrev-ref HEAD 2>/dev/null || echo local)"
fi
branch="${branch//\//-}"

backend_image="registry.local/template-backend"
frontend_image="registry.local/template-frontend"

docker build -f "$repo_root/docker/Dockerfile" --target backend -t "$backend_image:$sha" "$repo_root"
docker tag "$backend_image:$sha" "$backend_image:latest"
docker tag "$backend_image:$sha" "$backend_image:$branch"

docker build -f "$repo_root/docker/Dockerfile" --target frontend -t "$frontend_image:$sha" "$repo_root"
docker tag "$frontend_image:$sha" "$frontend_image:latest"
docker tag "$frontend_image:$sha" "$frontend_image:$branch"
