from apps.system.contracts.health import DependencyProbe, LivenessProbe, ReadinessProbe
from apps.system.contracts.meta import ServiceMetadata
from polyfactory.factories.pydantic_factory import ModelFactory


class ServiceMetadataFactory(ModelFactory[ServiceMetadata]):
    __model__ = ServiceMetadata


class LivenessProbeFactory(ModelFactory[LivenessProbe]):
    __model__ = LivenessProbe


class DependencyProbeFactory(ModelFactory[DependencyProbe]):
    __model__ = DependencyProbe


class ReadinessProbeFactory(ModelFactory[ReadinessProbe]):
    __model__ = ReadinessProbe
