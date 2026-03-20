import re
from functools import lru_cache

from opentelemetry import metrics

_SLUG_ROUTES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"^/projects/[^/]+$"), "/projects/{slug}"),
    (re.compile(r"^/blog/posts/[^/]+$"), "/blog/posts/{slug}"),
    (re.compile(r"^/blog/tags/[^/]+$"), "/blog/tags/{tag}"),
)


def _normalize_metric_path(path: str) -> str:
    for pattern, replacement in _SLUG_ROUTES:
        if pattern.match(path):
            return replacement
    return path


class AppMetrics:
    def __init__(self) -> None:
        meter = metrics.get_meter(__name__)
        self._requests_total = meter.create_counter(
            name="site.http.server.request.count",
            description="Total HTTP requests served.",
            unit="1",
        )
        self._request_duration_ms = meter.create_histogram(
            name="site.http.server.request.duration",
            description="HTTP request duration in milliseconds.",
            unit="ms",
        )
        self._requests_in_flight = meter.create_up_down_counter(
            name="site.http.server.active_requests",
            description="In-flight HTTP requests.",
            unit="1",
        )
        self._contact_submissions_total = meter.create_counter(
            name="site.contact.submission.count",
            description="Total contact submissions by outcome.",
            unit="1",
        )
        self._notification_duration_ms = meter.create_histogram(
            name="site.contact.notification.duration",
            description="Notification channel send duration in milliseconds.",
            unit="ms",
        )
        self._notification_total = meter.create_counter(
            name="site.contact.notification.count",
            description="Notification channel outcomes.",
            unit="1",
        )

    def request_started(self, *, method: str, path: str) -> None:
        normalized = _normalize_metric_path(path)
        self._requests_in_flight.add(
            1, attributes={"method": method, "path": normalized}
        )

    def request_finished(
        self,
        *,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        exception_class: str = "",
    ) -> None:
        normalized = _normalize_metric_path(path)
        attributes = {
            "method": method,
            "path": normalized,
            "status_code": str(status_code),
            "exception_class": exception_class or "none",
        }
        self._requests_total.add(1, attributes=attributes)
        self._request_duration_ms.record(duration_ms, attributes=attributes)
        self._requests_in_flight.add(
            -1, attributes={"method": method, "path": normalized}
        )

    def record_contact_submission(self, *, outcome: str) -> None:
        self._contact_submissions_total.add(1, attributes={"outcome": outcome})

    def record_notification(
        self, *, channel: str, outcome: str, duration_ms: float
    ) -> None:
        attributes = {"channel": channel, "outcome": outcome}
        self._notification_total.add(1, attributes=attributes)
        self._notification_duration_ms.record(duration_ms, attributes=attributes)


@lru_cache(maxsize=1)
def get_app_metrics() -> AppMetrics:
    return AppMetrics()
