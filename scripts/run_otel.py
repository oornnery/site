from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import settings


def _merge_resource_attributes(existing: str, additions: dict[str, str]) -> str:
    merged: dict[str, str] = {}

    for item in existing.split(","):
        raw = item.strip()
        if not raw or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        merged[key.strip()] = value.strip()

    for key, value in additions.items():
        if value:
            merged.setdefault(key, value)

    return ",".join(f"{key}={value}" for key, value in merged.items())


def build_otel_env(base_env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(base_env or os.environ)

    env.setdefault("OTEL_SERVICE_NAME", settings.telemetry_service_name)
    env.setdefault("OTEL_TRACES_EXPORTER", "otlp")
    env.setdefault("OTEL_METRICS_EXPORTER", "otlp")
    env.setdefault(
        "OTEL_LOGS_EXPORTER",
        "otlp" if settings.telemetry_logs_enabled else "none",
    )
    env.setdefault(
        "OTEL_EXPORTER_OTLP_INSECURE",
        str(settings.telemetry_exporter_otlp_insecure).lower(),
    )

    if settings.telemetry_exporter_otlp_endpoint:
        env.setdefault(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            settings.telemetry_exporter_otlp_endpoint,
        )
    if settings.telemetry_exporter_otlp_headers:
        env.setdefault(
            "OTEL_EXPORTER_OTLP_HEADERS",
            settings.telemetry_exporter_otlp_headers,
        )

    env["OTEL_RESOURCE_ATTRIBUTES"] = _merge_resource_attributes(
        env.get("OTEL_RESOURCE_ATTRIBUTES", ""),
        {
            "service.namespace": settings.telemetry_service_namespace,
            "deployment.environment": "development" if settings.debug else "production",
        },
    )
    return env


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run uvicorn under OpenTelemetry auto-instrumentation."
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default="8000")
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    command = [
        "opentelemetry-instrument",
        "uvicorn",
        "app.main:app",
        "--host",
        args.host,
        "--port",
        str(args.port),
    ]
    if args.reload:
        command.append("--reload")

    os.execvpe(command[0], command, build_otel_env())


if __name__ == "__main__":
    main()
