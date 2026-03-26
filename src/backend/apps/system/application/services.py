import asyncio
from dataclasses import dataclass
from typing import Literal

from core.observability import get_logger
from core.settings import Settings
from redis.exceptions import RedisError
from sqlalchemy.exc import SQLAlchemyError

from apps.system.contracts.health import DependencyProbe, LivenessProbe, ReadinessProbe
from apps.system.domain.ports import SystemHealthPort

SYSTEM_HEALTH_LOGGER = get_logger("apps.system.application.services")


@dataclass(slots=True, frozen=True)
class SystemStatusService:
    settings: Settings
    health_port: SystemHealthPort

    async def get_liveness(self) -> LivenessProbe:
        return LivenessProbe(status="ok", service=self.settings.app.name)

    async def get_readiness(self) -> ReadinessProbe:
        checks = list(
            await asyncio.gather(
                self._probe_database(),
                self._probe_redis(),
            )
        )
        status: Literal["ok", "error"] = "ok" if all(check.status == "ok" for check in checks) else "error"

        return ReadinessProbe(status=status, service=self.settings.app.name, checks=tuple(checks))

    async def _probe_database(self) -> DependencyProbe:
        try:
            await asyncio.wait_for(
                self.health_port.ping_database(),
                timeout=self.settings.system.health_timeout_seconds,
            )
        except TimeoutError:
            SYSTEM_HEALTH_LOGGER.warning(
                "System dependency probe timed out",
                dependency="postgres",
                timeout_seconds=self.settings.system.health_timeout_seconds,
                exc_info=True,
            )
            return DependencyProbe(name="postgres", status="error", detail="timeout")
        except OSError, SQLAlchemyError:
            SYSTEM_HEALTH_LOGGER.warning(
                "System dependency probe failed",
                dependency="postgres",
                timeout_seconds=self.settings.system.health_timeout_seconds,
                exc_info=True,
            )
            return DependencyProbe(name="postgres", status="error", detail="database unavailable")

        return DependencyProbe(name="postgres", status="ok")

    async def _probe_redis(self) -> DependencyProbe:
        try:
            await asyncio.wait_for(
                self.health_port.ping_redis(),
                timeout=self.settings.system.health_timeout_seconds,
            )
        except TimeoutError:
            SYSTEM_HEALTH_LOGGER.warning(
                "System dependency probe timed out",
                dependency="redis",
                timeout_seconds=self.settings.system.health_timeout_seconds,
                exc_info=True,
            )
            return DependencyProbe(name="redis", status="error", detail="timeout")
        except OSError, RedisError:
            SYSTEM_HEALTH_LOGGER.warning(
                "System dependency probe failed",
                dependency="redis",
                timeout_seconds=self.settings.system.health_timeout_seconds,
                exc_info=True,
            )
            return DependencyProbe(name="redis", status="error", detail="redis unavailable")

        return DependencyProbe(name="redis", status="ok")
