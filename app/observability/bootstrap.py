from __future__ import annotations

from typing import Any

from opentelemetry import _logs as otel_logs, metrics, trace

from app.core.config import settings

_PROXY_PROVIDER_NAMES = frozenset(
    {
        "ProxyTracerProvider",
        "_ProxyMeterProvider",
        "ProxyLoggerProvider",
    }
)


def _is_proxy_provider(provider: object) -> bool:
    return type(provider).__name__ in _PROXY_PROVIDER_NAMES


def _resource_updates() -> dict[str, str]:
    return {
        "service.name": settings.telemetry_service_name.strip(),
        "service.namespace": settings.telemetry_service_namespace.strip(),
        "deployment.environment": "development" if settings.debug else "production",
    }


def _mutable_resource_attrs(resource: object) -> Any | None:
    attrs = getattr(resource, "_attributes", None)
    if attrs is None or not hasattr(attrs, "_dict"):
        return None
    return attrs


def _should_override_service_name(current_value: object) -> bool:
    service_name = str(current_value or "").strip()
    return not service_name or service_name.startswith("unknown_service")


def _patch_resource(resource: object) -> bool:
    attrs = _mutable_resource_attrs(resource)
    if attrs is None:
        return False

    current_attrs = getattr(resource, "attributes", {})
    updates = _resource_updates()
    pending: dict[str, str] = {}

    if _should_override_service_name(current_attrs.get("service.name")):
        pending["service.name"] = updates["service.name"]
    for key in ("service.namespace", "deployment.environment"):
        if not str(current_attrs.get(key, "")).strip():
            pending[key] = updates[key]

    if not pending:
        return False

    was_immutable = getattr(attrs, "_immutable", True)
    attrs._immutable = False
    try:
        for key, value in pending.items():
            attrs[key] = value
    finally:
        attrs._immutable = was_immutable

    return True


def _provider_resource(provider: object) -> object | None:
    resource = getattr(provider, "resource", None)
    if resource is not None:
        return resource

    sdk_config = getattr(provider, "_sdk_config", None)
    if sdk_config is None:
        return None
    return getattr(sdk_config, "resource", None)


def configure_auto_instrumentation_resources() -> bool:
    updated = False

    for provider in (
        trace.get_tracer_provider(),
        metrics.get_meter_provider(),
        otel_logs.get_logger_provider(),
    ):
        if _is_proxy_provider(provider):
            continue
        resource = _provider_resource(provider)
        if resource is None:
            continue
        updated = _patch_resource(resource) or updated

    return updated
