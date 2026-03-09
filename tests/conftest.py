import os
from collections.abc import Iterator

import pytest

os.environ["DEBUG"] = "false"
os.environ["SECRET_KEY"] = "test-secret-key-with-sufficient-length"
os.environ["TELEMETRY_ENABLED"] = "false"
os.environ["FRONTEND_TELEMETRY_ENABLED"] = "false"


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> Iterator[None]:
    from app.core.dependencies import limiter

    limiter.reset()
    yield
    limiter.reset()
