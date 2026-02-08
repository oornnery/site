from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Use isolated DB for tests before importing apps/settings.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test-site.db")
os.environ.setdefault("SEED_DB_ON_STARTUP", "true")

from apps.admin.app import app as admin_app
from apps.blog.app import app as blog_app
from apps.portfolio.app import app as portfolio_app


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    db_path = Path("test-site.db")
    if db_path.exists():
        db_path.unlink()
    yield
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def portfolio():
    with TestClient(portfolio_app) as client:
        yield client


@pytest.fixture
def blog():
    with TestClient(blog_app) as client:
        yield client


@pytest.fixture
def admin():
    with TestClient(admin_app) as client:
        yield client


@pytest.fixture(params=["portfolio", "blog", "admin"])
def client(request, portfolio, blog, admin):
    return {"portfolio": portfolio, "blog": blog, "admin": admin}[request.param]
