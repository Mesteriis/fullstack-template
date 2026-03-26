from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FRONTEND_ROOT = ROOT / "src" / "frontend"


def main() -> int:
    lint_result = subprocess.run(["pnpm", "lint"], cwd=FRONTEND_ROOT)
    if lint_result.returncode != 0:
        return lint_result.returncode

    architecture_result = subprocess.run([sys.executable, "scripts/check_frontend_architecture.py"], cwd=ROOT)
    return architecture_result.returncode


if __name__ == "__main__":
    sys.exit(main())
