from pytest_alembic.runner import MigrationContext


def test_migrations_upgrade_downgrade_roundtrip(alembic_runner: MigrationContext) -> None:
    alembic_runner.migrate_up_to("head")
    alembic_runner.migrate_down_to("base")
    alembic_runner.migrate_up_to("head")
