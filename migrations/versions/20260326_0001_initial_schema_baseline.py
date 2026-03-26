"""Initial schema baseline.

Revision ID: 20260326_0001
Revises:
Create Date: 2026-03-26 16:40:00
"""

from __future__ import annotations

from collections.abc import Sequence

revision: str = "20260326_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Create the baseline revision for template-owned migrations."""


def downgrade() -> None:
    """Return to the pre-template migration baseline."""
