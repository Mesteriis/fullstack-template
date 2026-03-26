from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    result = subprocess.run(["uv", "run", "pytest", "-x", "-q", "--test-alembic"], cwd=ROOT / "src" / "backend")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
