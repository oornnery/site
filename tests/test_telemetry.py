from __future__ import annotations

from fastapi import FastAPI
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

import app.observability.bootstrap as bootstrap
import app.observability.telemetry as telemetry
from app.core.config import Settings


class ProxyTracerProvider:
    pass


class ProxyLoggerProvider:
    pass


class _ProxyMeterProvider:
    pass


class ExistingTracerProvider:
    pass


class ExistingMeterProvider:
    pass


class ExistingLoggerProvider:
    pass


def test_configure_telemetry_sets_providers_when_globals_are_proxies(
    monkeypatch,
) -> None:
    app = FastAPI()
    calls: list[str] = []

    monkeypatch.setattr(telemetry, "_configured", False)
    monkeypatch.setattr(telemetry.settings, "telemetry_enabled", True)
    monkeypatch.setattr(telemetry, "_build_resource", lambda: object())
    monkeypatch.setattr(
        telemetry.trace,
        "get_tracer_provider",
        lambda: ProxyTracerProvider(),
    )
    monkeypatch.setattr(
        telemetry.metrics,
        "get_meter_provider",
        lambda: _ProxyMeterProvider(),
    )
    monkeypatch.setattr(
        telemetry.otel_logs,
        "get_logger_provider",
        lambda: ProxyLoggerProvider(),
    )
    monkeypatch.setattr(
        telemetry,
        "_configure_tracing",
        lambda resource: calls.append("trace"),
    )
    monkeypatch.setattr(
        telemetry,
        "_configure_metrics",
        lambda resource: calls.append("metrics"),
    )
    monkeypatch.setattr(
        telemetry,
        "_configure_logs",
        lambda resource: calls.append("logs"),
    )
    monkeypatch.setattr(
        telemetry,
        "_instrument_fastapi",
        lambda current_app: calls.append("fastapi"),
    )
    monkeypatch.setattr(
        telemetry,
        "_instrument_httpx",
        lambda: calls.append("httpx"),
    )

    telemetry.configure_telemetry(app)

    assert calls == ["trace", "metrics", "logs", "fastapi", "httpx"]


def test_configure_telemetry_reuses_preconfigured_global_providers(monkeypatch) -> None:
    app = FastAPI()
    calls: list[str] = []

    monkeypatch.setattr(telemetry, "_configured", False)
    monkeypatch.setattr(telemetry.settings, "telemetry_enabled", True)
    monkeypatch.setattr(telemetry, "_build_resource", lambda: object())
    monkeypatch.setattr(
        telemetry.trace,
        "get_tracer_provider",
        lambda: ExistingTracerProvider(),
    )
    monkeypatch.setattr(
        telemetry.metrics,
        "get_meter_provider",
        lambda: ExistingMeterProvider(),
    )
    monkeypatch.setattr(
        telemetry.otel_logs,
        "get_logger_provider",
        lambda: ExistingLoggerProvider(),
    )
    monkeypatch.setattr(
        telemetry,
        "_configure_tracing",
        lambda resource: calls.append("trace"),
    )
    monkeypatch.setattr(
        telemetry,
        "_configure_metrics",
        lambda resource: calls.append("metrics"),
    )
    monkeypatch.setattr(
        telemetry,
        "_configure_logs",
        lambda resource: calls.append("logs"),
    )
    monkeypatch.setattr(
        telemetry,
        "_instrument_fastapi",
        lambda current_app: calls.append("fastapi"),
    )
    monkeypatch.setattr(
        telemetry,
        "_instrument_httpx",
        lambda: calls.append("httpx"),
    )

    telemetry.configure_telemetry(app)

    assert calls == ["logs", "fastapi", "httpx"]


def test_frontend_telemetry_collector_endpoint_is_derived_from_backend_otlp() -> None:
    settings = Settings(
        secret_key="test-secret-key-with-sufficient-length",
        telemetry_exporter_otlp_endpoint="http://localhost:4317",
    )

    assert settings.frontend_telemetry_collector_endpoint() == (
        "http://localhost:4318/v1/traces"
    )


def test_frontend_telemetry_browser_endpoint_uses_same_origin_proxy() -> None:
    settings = Settings(
        secret_key="test-secret-key-with-sufficient-length",
        frontend_telemetry_enabled=True,
        telemetry_exporter_otlp_endpoint="http://localhost:4317",
    )

    assert settings.frontend_telemetry_is_enabled() is True
    assert settings.frontend_telemetry_browser_endpoint() == "/otel/v1/traces"


def test_auto_instrumentation_resource_defaults_replace_unknown_service_name(
    monkeypatch,
) -> None:
    tracer_provider = TracerProvider(
        resource=Resource.create({"service.name": "unknown_service"})
    )
    meter_provider = MeterProvider(
        resource=Resource.create({"service.name": "unknown_service"})
    )
    logger_provider = LoggerProvider(
        resource=Resource.create({"service.name": "unknown_service"})
    )

    monkeypatch.setattr(
        bootstrap.trace,
        "get_tracer_provider",
        lambda: tracer_provider,
    )
    monkeypatch.setattr(
        bootstrap.metrics,
        "get_meter_provider",
        lambda: meter_provider,
    )
    monkeypatch.setattr(
        bootstrap.otel_logs,
        "get_logger_provider",
        lambda: logger_provider,
    )
    monkeypatch.setattr(
        bootstrap.settings,
        "telemetry_service_name",
        "portfolio-backend",
    )
    monkeypatch.setattr(
        bootstrap.settings,
        "telemetry_service_namespace",
        "portfolio",
    )
    monkeypatch.setattr(bootstrap.settings, "debug", True)

    assert bootstrap.configure_auto_instrumentation_resources() is True
    assert tracer_provider.resource.attributes["service.name"] == "portfolio-backend"
    assert tracer_provider.resource.attributes["service.namespace"] == "portfolio"
    assert (
        tracer_provider.resource.attributes["deployment.environment"] == "development"
    )
    assert (
        meter_provider._sdk_config.resource.attributes["service.name"]
        == "portfolio-backend"
    )
    assert logger_provider.resource.attributes["service.name"] == "portfolio-backend"
