# Infrastructure Observability Assets

This directory stores operational observability artifacts for SigNoz.
Grafana- and Prometheus-specific assets were removed from this repository.

## Contents

- `signoz/dashboards/portfolio-backend-overview.json`
  - Backend service health dashboard built from app-level OpenTelemetry metrics.
- `signoz/dashboards/portfolio-frontend-telemetry.json`
  - Frontend tracing and OTLP proxy dashboard for browser telemetry.
- `signoz/alerts/*.json`
  - Alert rule manifests for the SigNoz `/api/v1/rules` API.
- `signoz/README.md`
  - Import runbook for dashboards and alerts.

## Runtime dependencies

These assets assume the application is exporting telemetry through
OpenTelemetry, as configured in the app settings.

## SigNoz setup (logs, metrics, traces)

Configure the application environment with OTLP endpoint values.

For local SigNoz (default OTLP gRPC):

```env
TELEMETRY_ENABLED=true
TELEMETRY_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
TELEMETRY_EXPORTER_OTLP_INSECURE=true
TELEMETRY_LOGS_ENABLED=true
FRONTEND_TELEMETRY_ENABLED=true
```

For SigNoz Cloud, include auth headers:

```env
TELEMETRY_ENABLED=true
TELEMETRY_EXPORTER_OTLP_ENDPOINT=https://ingest.<region>.signoz.cloud:443
TELEMETRY_EXPORTER_OTLP_INSECURE=false
TELEMETRY_LOGS_ENABLED=true
FRONTEND_TELEMETRY_ENABLED=true
TELEMETRY_EXPORTER_OTLP_HEADERS=signoz-ingestion-key=<your-key>
```

## Validation checklist

1. Start the app and hit `/`, `/about`, `/projects`, `/contact`.
2. Open SigNoz and confirm services `portfolio-backend` and
   `portfolio-frontend` appear.
3. Verify traces, metrics, and logs are ingesting.
4. Confirm `POST /otel/v1/traces` traffic appears in the frontend dashboard.
5. Import the dashboards and alerts from `infra/signoz/`.

Detailed import instructions live in `infra/signoz/README.md`.

## Refs

- OpenTelemetry Python docs:
  <https://opentelemetry.io/docs/languages/python/>
- OpenTelemetry JS docs:
  <https://opentelemetry.io/docs/languages/js/>
- SigNoz dashboards repo:
  <https://github.com/SigNoz/dashboards>
- SigNoz API docs:
  <https://github.com/SigNoz/signoz/blob/main/docs/api/openapi.yml>
