#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

run_local_trivy() {
  trivy fs \
    --exit-code 1 \
    --no-progress \
    --scanners vuln,secret,misconfig \
    --skip-dirs "$repo_root/src/backend/.venv" \
    --skip-dirs "$repo_root/src/frontend/node_modules" \
    --skip-dirs "$repo_root/src/frontend/dist" \
    "$repo_root"
}

run_docker_trivy() {
  docker run --rm \
    -v "$repo_root:/workspace" \
    aquasec/trivy:latest \
    fs \
    --exit-code 1 \
    --no-progress \
    --scanners vuln,secret,misconfig \
    --skip-dirs /workspace/src/backend/.venv \
    --skip-dirs /workspace/src/frontend/node_modules \
    --skip-dirs /workspace/src/frontend/dist \
    /workspace
}

if command -v trivy >/dev/null 2>&1; then
  run_local_trivy
  exit 0
fi

run_docker_trivy
