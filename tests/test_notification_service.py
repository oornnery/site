import asyncio
from unittest.mock import AsyncMock

from app.infrastructure.notifications.email import (
    ContactNotificationContext,
    ContactNotificationService,
    NotificationChannelResult,
    NotificationDispatchResult,
)
from app.models.contact import ContactForm
from app.observability.metrics import AppMetrics


def _make_contact() -> ContactForm:
    return ContactForm(
        name="Test User",
        email="test@example.com",
        subject="Test Subject",
        message="This is a test message for notification.",
        csrf_token="fake-csrf-token",
    )


def _make_context() -> ContactNotificationContext:
    return ContactNotificationContext(
        request_id="test-req-123",
        client_ip="127.0.0.1",
    )


def _make_noop_metrics() -> AppMetrics:
    m = AppMetrics()
    return m


def test_dispatch_result_any_success() -> None:
    result = NotificationDispatchResult(
        results=(
            NotificationChannelResult(channel="webhook", success=True),
            NotificationChannelResult(channel="email", success=False, error="Failed"),
        )
    )
    assert result.any_success is True
    assert result.all_failed is False
    assert result.has_channels is True


def test_dispatch_result_all_failed() -> None:
    result = NotificationDispatchResult(
        results=(
            NotificationChannelResult(channel="webhook", success=False, error="err"),
            NotificationChannelResult(channel="email", success=False, error="err"),
        )
    )
    assert result.any_success is False
    assert result.all_failed is True


def test_dispatch_result_all_skipped() -> None:
    result = NotificationDispatchResult(
        results=(
            NotificationChannelResult(
                channel="webhook",
                success=False,
                error="Webhook channel is not configured.",
            ),
            NotificationChannelResult(
                channel="email", success=False, error="Email channel is not configured."
            ),
        )
    )
    assert result.all_skipped is True
    assert result.all_failed is True


def test_dispatch_result_empty() -> None:
    result = NotificationDispatchResult(results=())
    assert result.has_channels is False
    assert result.any_success is False
    assert result.all_failed is False


def test_notification_service_handles_channel_exception() -> None:
    channel = AsyncMock()
    channel.send.side_effect = RuntimeError("Boom")
    channel.__class__.__name__ = "TestChannel"

    service = ContactNotificationService(
        channels=[channel], metrics=_make_noop_metrics()
    )
    result = asyncio.run(
        service.notify_submission(
            contact=_make_contact(),
            context=_make_context(),
        )
    )
    assert result.has_channels is True
    assert result.all_failed is True
    assert "RuntimeError" in result.results[0].error


def test_notification_service_returns_empty_for_no_channels() -> None:
    service = ContactNotificationService(channels=[], metrics=_make_noop_metrics())
    result = asyncio.run(
        service.notify_submission(
            contact=_make_contact(),
            context=_make_context(),
        )
    )
    assert result.has_channels is False
    assert result.results == ()
