import pytest
from fastapi.testclient import TestClient

from apps.portfolio.app import app as portfolio_app
from apps.blog.app import app as blog_app
from apps.admin.app import app as admin_app


@pytest.fixture
def portfolio():
    return TestClient(portfolio_app)


@pytest.fixture
def blog():
    return TestClient(blog_app)


@pytest.fixture
def admin():
    return TestClient(admin_app)


@pytest.fixture(params=["portfolio", "blog", "admin"])
def client(request, portfolio, blog, admin):
    """Parametrized fixture that yields each app's TestClient in turn."""
    return {"portfolio": portfolio, "blog": blog, "admin": admin}[request.param]
