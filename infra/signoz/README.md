# SigNoz Dashboards and Alerts

These assets are designed for the telemetry emitted by this repository:

- backend service name: `portfolio-backend`
- frontend service name: `portfolio-frontend`
- frontend browser ingestion path: `POST /otel/v1/traces`

If you changed `TELEMETRY_SERVICE_NAME` or `FRONTEND_TELEMETRY_SERVICE_NAME`,
replace those service names in the JSON manifests before importing.

## Dashboards

Import the JSON files from `infra/signoz/dashboards/` in the SigNoz UI.

1. Open SigNoz.
2. Go to `Dashboards`.
3. Choose the import option in the dashboard UI.
4. Import:
   - `portfolio-backend-overview.json`
   - `portfolio-frontend-telemetry.json`

What they cover:

- `portfolio-backend-overview.json`
  - request rate, p95 latency, 5xx ratio, in-flight requests
  - contact submission outcomes
  - notification outcomes and notification latency
- `portfolio-frontend-telemetry.json`
  - frontend span throughput and p95 latency
  - frontend error ratio and errored operations
  - OTLP proxy traffic and OTLP proxy 5xx ratio

## Alerts

The alert manifests under `infra/signoz/alerts/` are ready for the
`/api/v1/rules` endpoint, but they intentionally use the placeholder channel
name `__REPLACE_WITH_SIGNOZ_CHANNEL__`.

Use an existing SigNoz notification channel name when importing.

Example import loop:

```bash
export SIGNOZ_BASE_URL=http://localhost:8080
export SIGNOZ_API_TOKEN=<your-signoz-api-token>
export SIGNOZ_CHANNEL=<existing-signoz-channel-name>

for rule in infra/signoz/alerts/*.json; do
  jq --arg channel "$SIGNOZ_CHANNEL" \
    '(.condition.thresholds.spec[]?.channels) |= [$channel]' \
    "$rule" \
    | curl -sS \
        -X POST "$SIGNOZ_BASE_URL/api/v1/rules" \
        -H "Authorization: Bearer $SIGNOZ_API_TOKEN" \
        -H "Content-Type: application/json" \
        --data-binary @-
done
```

Included rules:

- `backend-high-5xx-rate.json`
- `backend-high-p95-latency.json`
- `contact-delivery-degraded.json`
- `frontend-high-error-rate.json`
- `frontend-otlp-proxy-failures.json`

## Signal assumptions

Backend metrics come from the app meter:

- `portfolio.http.requests_total`
- `portfolio.http.request_duration_ms`
- `portfolio.http.requests_in_flight`
- `portfolio.contact.submissions_total`
- `portfolio.contact.notification_total`
- `portfolio.contact.notification_duration_ms`

Frontend panels and alerts use SigNoz trace-derived metrics:

- `signoz_calls_total`
- `signoz_latency.bucket`

The OTLP proxy panels and alerts use backend request metrics filtered on:

- `path="/otel/v1/traces"`
