import logging
from collections.abc import Mapping
from typing import Any, cast

from fastapi import FastAPI
from opentelemetry import _logs as otel_logs, metrics, trace
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    ConsoleLogRecordExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

from app.core.config import settings
from app.observability.bootstrap import configure_auto_instrumentation_resources

logger = logging.getLogger(__name__)

_configured = False
_otel_log_handler_attached = False
_PROXY_PROVIDER_NAMES = frozenset(
    {
        "ProxyTracerProvider",
        "_ProxyMeterProvider",
        "ProxyLoggerProvider",
    }
)


def _is_proxy_provider(provider: object) -> bool:
    return type(provider).__name__ in _PROXY_PROVIDER_NAMES


def _has_global_tracer_provider() -> bool:
    return not _is_proxy_provider(trace.get_tracer_provider())


def _has_global_meter_provider() -> bool:
    return not _is_proxy_provider(metrics.get_meter_provider())


def _has_global_logger_provider() -> bool:
    return not _is_proxy_provider(otel_logs.get_logger_provider())


def _otlp_headers() -> str | None:
    headers = settings.telemetry_exporter_otlp_headers.strip()
    return headers or None


def _build_resource() -> Resource:
    return Resource.create(
        {
            "service.name": settings.telemetry_service_name,
            "service.namespace": settings.telemetry_service_namespace,
            "deployment.environment": "development" if settings.debug else "production",
        }
    )


def _attach_logging_handler(logger_provider: object) -> None:
    global _otel_log_handler_attached
    if _otel_log_handler_attached:
        return

    logging.getLogger().addHandler(
        LoggingHandler(
            level=logging.NOTSET,
            logger_provider=cast(Any, logger_provider),
        )
    )
    _otel_log_handler_attached = True
    logger.info("OpenTelemetry logging handler attached to root logger.")


def _configure_tracing(resource: Resource) -> None:
    tracer_provider = TracerProvider(
        resource=resource,
        sampler=ParentBased(TraceIdRatioBased(settings.telemetry_traces_sample_ratio)),
    )
    headers = _otlp_headers()

    if settings.telemetry_exporter_otlp_endpoint:
        tracer_provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=settings.telemetry_exporter_otlp_endpoint,
                    insecure=settings.telemetry_exporter_otlp_insecure,
                    headers=headers,
                )
            )
        )
        logger.info(
            "Tracing exporter configured with OTLP endpoint=%s.",
            settings.telemetry_exporter_otlp_endpoint,
        )
    elif settings.telemetry_console_exporters:
        tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        logger.info("Tracing exporter configured with console output.")

    trace.set_tracer_provider(tracer_provider)


def _configure_metrics(resource: Resource) -> None:
    metric_readers: list[PeriodicExportingMetricReader] = []
    headers = _otlp_headers()

    if settings.telemetry_exporter_otlp_endpoint:
        metric_readers.append(
            PeriodicExportingMetricReader(
                OTLPMetricExporter(
                    endpoint=settings.telemetry_exporter_otlp_endpoint,
                    insecure=settings.telemetry_exporter_otlp_insecure,
                    headers=headers,
                )
            )
        )
        logger.info(
            "Metric exporter configured with OTLP endpoint=%s.",
            settings.telemetry_exporter_otlp_endpoint,
        )
    elif settings.telemetry_console_exporters:
        metric_readers.append(
            PeriodicExportingMetricReader(
                ConsoleMetricExporter(),
                export_interval_millis=15000,
            )
        )

    metrics.set_meter_provider(
        MeterProvider(resource=resource, metric_readers=metric_readers)
    )


def _configure_logs(resource: Resource) -> None:
    if not settings.telemetry_logs_enabled:
        logger.info("Telemetry log export is disabled by configuration.")
        return

    if _has_global_logger_provider():
        logger.info(
            "Detected pre-configured OpenTelemetry logger provider; reusing it."
        )
        _attach_logging_handler(otel_logs.get_logger_provider())
        return

    logger_provider = LoggerProvider(resource=resource)
    headers = _otlp_headers()

    if settings.telemetry_exporter_otlp_endpoint:
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(
                OTLPLogExporter(
                    endpoint=settings.telemetry_exporter_otlp_endpoint,
                    insecure=settings.telemetry_exporter_otlp_insecure,
                    headers=headers,
                )
            )
        )
        logger.info(
            "Log exporter configured with OTLP endpoint=%s.",
            settings.telemetry_exporter_otlp_endpoint,
        )
    elif settings.telemetry_console_exporters:
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(ConsoleLogRecordExporter())
        )
        logger.info("Log exporter configured with console output.")
    else:
        logger.info(
            "Telemetry log exporter is not configured; OTLP endpoint is empty and console exporters are disabled."
        )
        return

    otel_logs.set_logger_provider(logger_provider)
    _attach_logging_handler(logger_provider)


def add_current_span_event(
    name: str,
    attributes: Mapping[str, str | int | float | bool] | None = None,
) -> None:
    span = trace.get_current_span()
    if not span.is_recording():
        return
    span.add_event(name, attributes=dict(attributes or {}))


def set_current_span_attributes(
    attributes: Mapping[str, str | int | float | bool],
) -> None:
    span = trace.get_current_span()
    if not span.is_recording():
        return
    span.set_attributes(dict(attributes))


def _instrument_fastapi(app: FastAPI) -> None:
    if getattr(app, "_is_instrumented_by_opentelemetry", False):
        logger.info("FastAPI app already instrumented; skipping local instrumentation.")
        return
    FastAPIInstrumentor.instrument_app(app, excluded_urls="/static,/favicon.ico")


def _instrument_httpx() -> None:
    instrumentor = HTTPXClientInstrumentor()
    if instrumentor.is_instrumented_by_opentelemetry:
        logger.info("HTTPX already instrumented; skipping local instrumentation.")
        return
    instrumentor.instrument()


def configure_telemetry(app: FastAPI) -> None:
    global _configured
    if _configured:
        return

    if not settings.telemetry_enabled:
        logger.info("Telemetry is disabled by configuration.")
        return

    if configure_auto_instrumentation_resources():
        logger.info(
            "Applied project telemetry resource defaults to pre-configured OpenTelemetry providers."
        )

    resource = _build_resource()

    if _has_global_tracer_provider():
        logger.info(
            "Detected pre-configured OpenTelemetry tracer provider; reusing it."
        )
    else:
        _configure_tracing(resource)

    if _has_global_meter_provider():
        logger.info("Detected pre-configured OpenTelemetry meter provider; reusing it.")
    else:
        _configure_metrics(resource)

    _configure_logs(resource)
    _instrument_fastapi(app)
    _instrument_httpx()

    _configured = True
    logger.info("OpenTelemetry configured successfully.")
