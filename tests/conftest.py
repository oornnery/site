import os
from collections.abc import Iterator

import pytest

os.environ["DEBUG"] = "false"
os.environ["SECRET_KEY"] = "test-secret-key-with-sufficient-length"
os.environ["FRONTEND_TELEMETRY_ENABLED"] = "false"


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> Iterator[None]:
    from app.core.deps import limiter

    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture(autouse=True)
def _clear_content_caches() -> Iterator[None]:
    from app.infrastructure.markdown import _content_cache

    _content_cache.clear()
    yield
    _content_cache.clear()
