"""Smoke tests for all three apps (portfolio, blog, admin).

Each test runs against all apps via the parametrized `client` fixture.
"""


class TestHomePage:
    def test_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_contains_online_badge(self, client):
        r = client.get("/")
        assert "Online" in r.text

    def test_contains_status_link(self, client):
        r = client.get("/")
        assert "/status" in r.text

    def test_includes_frontend_libs(self, client):
        r = client.get("/")
        assert "htmx.org" in r.text
        assert "alpinejs" in r.text
        assert "tailwindcss" in r.text

    def test_dark_mode_support(self, client):
        r = client.get("/")
        assert "dark:bg-zinc-950" in r.text


class TestHealthzAPI:
    def test_returns_ok(self, client):
        r = client.get("/api/healthz")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "OK"
        assert data["code"] == 200
        assert "datetime" in data


class TestStatusPage:
    def test_returns_200(self, client):
        r = client.get("/status")
        assert r.status_code == 200

    def test_contains_summary_div(self, client):
        r = client.get("/status")
        assert 'id="healthz-summary"' in r.text

    def test_contains_refresh_button(self, client):
        r = client.get("/status")
        assert "Refresh" in r.text

    def test_has_auto_polling(self, client):
        r = client.get("/status")
        assert "every 10s" in r.text


class TestNotFoundHandler:
    def test_html_404(self, client):
        r = client.get("/does-not-exist")
        assert r.status_code == 404
        assert "404" in r.text
        assert "Go back" in r.text

    def test_json_404_for_api(self, client):
        r = client.get("/api/nope", headers={"accept": "application/json"})
        assert r.status_code == 404
        assert r.json() == {"detail": "Not Found"}


class TestHealthLogs:
    def test_logs_endpoint(self, client):
        r = client.get("/healthz/logs?service_id=portfolio")
        assert r.status_code == 200
        assert "portfolio" in r.text
