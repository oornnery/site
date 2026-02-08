from __future__ import annotations

import re


def test_healthz_all_apps(client):
    response = client.get("/api/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "OK"
    assert payload["code"] == 200


def test_status_page_all_apps(client):
    response = client.get("/status")
    assert response.status_code == 200
    assert "healthz-summary" in response.text


def test_json_404_all_apps(client):
    response = client.get("/api/does-not-exist", headers={"accept": "application/json"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_portfolio_home_has_no_blog_cards(portfolio):
    response = portfolio.get("/")
    assert response.status_code == 200
    assert "Latest Posts" not in response.text


def test_portfolio_home_shows_four_project_cards(portfolio):
    response = portfolio.get("/")
    assert response.status_code == 200
    project_links = set(re.findall(r'href="/projects/([a-z0-9-]+)"', response.text))
    assert len(project_links) >= 4


def test_portfolio_home_uses_about_summary_and_about_page_uses_full_markdown(portfolio):
    home = portfolio.get("/")
    assert home.status_code == 200
    assert "Building reliable web products with Python, FastAPI, and SSR-first UX." in home.text
    assert "https://github.com/oornnery" in home.text

    about = portfolio.get("/about")
    assert about.status_code == 200
    assert "Focused on clean architecture, performance, and pragmatic UX." in about.text
    assert "Building reliable web products with Python, FastAPI, and SSR-first UX." not in about.text


def test_portfolio_home_contact_connect_renders_icons(portfolio):
    home = portfolio.get("/")
    assert home.status_code == 200
    connect_idx = home.text.find("Connect")
    assert connect_idx != -1
    contact_chunk = home.text[connect_idx : connect_idx + 3000]
    assert "<svg" in contact_chunk
    assert "GitHub" in contact_chunk


def test_portfolio_contact_page_connect_renders_icons(portfolio):
    contact = portfolio.get("/contact")
    assert contact.status_code == 200
    connect_idx = contact.text.find("Connect")
    assert connect_idx != -1
    connect_chunk = contact.text[connect_idx : connect_idx + 3000]
    assert "<svg" in connect_chunk
    assert "GitHub" in connect_chunk


def test_portfolio_navbar_has_blog_link_without_login(portfolio):
    response = portfolio.get("/")
    assert response.status_code == 200
    assert "Blog" in response.text
    assert ">Login<" not in response.text


def test_portfolio_old_monolith_routes_are_404(portfolio):
    assert portfolio.get("/blog").status_code == 404
    assert portfolio.get("/login").status_code == 404
    assert portfolio.get("/admin").status_code == 404


def test_portfolio_api_projects_and_profile(portfolio):
    projects = portfolio.get("/api/projects")
    assert projects.status_code == 200
    assert isinstance(projects.json(), list)

    profile = portfolio.get("/api/profile")
    assert profile.status_code == 200
    assert "name" in profile.json()


def test_portfolio_contact_api(portfolio):
    response = portfolio.post(
        "/api/contact",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "message": "Hello from automated test message.",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["success"] is True


def test_portfolio_contact_partial_returns_validation_errors_without_500(portfolio):
    response = portfolio.post(
        "/partials/contact/form",
        data={
            "name": "A",
            "email": "invalid-email",
            "message": "short",
        },
    )
    assert response.status_code == 400
    assert "Name must have at least 2 characters" in response.text
    assert "Valid email is required" in response.text
    assert "Message must have at least 10 characters" in response.text


def test_blog_home_and_posts(blog):
    home = blog.get("/")
    assert home.status_code == 200
    assert "Explore posts" in home.text
    assert "min read" in home.text

    posts = blog.get("/posts")
    assert posts.status_code == 200
    assert "Search posts" in posts.text
    assert "min read" in posts.text

    api_posts = blog.get("/api/posts")
    assert api_posts.status_code == 200
    data = api_posts.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_blog_post_detail_and_comments_flow(blog):
    posts = blog.get("/api/posts").json()
    slug = posts[0]["slug"]

    detail = blog.get(f"/posts/{slug}")
    assert detail.status_code == 200

    comments_before = blog.get(f"/api/comments/{slug}")
    assert comments_before.status_code == 200
    before_count = len(comments_before.json())

    create = blog.post(
        f"/api/comments/{slug}",
        json={
            "content": "Great article from test suite.",
            "guest_name": "Guest Tester",
            "guest_email": "guest@example.com",
        },
    )
    assert create.status_code == 200

    comments_after = blog.get(f"/api/comments/{slug}")
    assert comments_after.status_code == 200
    assert len(comments_after.json()) >= before_count


def test_blog_reactions_api(blog):
    posts = blog.get("/api/posts").json()
    slug = posts[0]["slug"]
    response = blog.post(f"/api/posts/{slug}/reactions", json={"type": "like"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "like"


def test_admin_root_redirects_to_login_when_unauthenticated(admin):
    response = admin.get("/", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/login"


def test_admin_login_page(admin):
    response = admin.get("/login")
    assert response.status_code == 200
    assert "Sign in" in response.text or "Welcome Back" in response.text


def test_admin_web_login_redirects_to_dashboard(admin):
    response = admin.post(
        "/login",
        data={"email": "admin@example.com", "password": "admin123"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"


def test_admin_auth_login_and_me(admin):
    login = admin.post(
        "/api/auth/login",
        data={"email": "admin@example.com", "password": "admin123"},
    )
    assert login.status_code == 200
    assert login.json()["ok"] is True

    me = admin.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "admin@example.com"


def test_admin_protected_pages_after_login(admin):
    admin.post(
        "/api/auth/login",
        data={"email": "admin@example.com", "password": "admin123"},
    )

    dashboard = admin.get("/admin")
    assert dashboard.status_code == 200

    analytics = admin.get("/api/analytics/pageviews")
    assert analytics.status_code == 200

    audit = admin.get("/api/audit")
    assert audit.status_code == 200


def test_admin_project_edit_page_renders(admin):
    admin.post(
        "/api/auth/login",
        data={"email": "admin@example.com", "password": "admin123"},
    )

    listing = admin.get("/admin/projects")
    assert listing.status_code == 200

    match = re.search(r"/admin/projects/([0-9a-f-]{36})", listing.text)
    assert match is not None

    detail = admin.get(f"/admin/projects/{match.group(1)}")
    assert detail.status_code == 200
    assert "Content (Markdown)" in detail.text


def test_admin_blog_edit_page_renders(admin):
    admin.post(
        "/api/auth/login",
        data={"email": "admin@example.com", "password": "admin123"},
    )

    listing = admin.get("/admin/blog")
    assert listing.status_code == 200

    match = re.search(r"/admin/blog/([0-9a-f-]{36})", listing.text)
    assert match is not None

    detail = admin.get(f"/admin/blog/{match.group(1)}")
    assert detail.status_code == 200
    assert "Content (Markdown)" in detail.text


def test_admin_profile_page_renders(admin):
    admin.post(
        "/api/auth/login",
        data={"email": "admin@example.com", "password": "admin123"},
    )

    response = admin.get("/admin/profile")
    assert response.status_code == 200
    assert "Social Links" in response.text


def test_admin_messages_lists_contact_messages(admin, portfolio):
    sent = portfolio.post(
        "/api/contact",
        json={
            "name": "Inbox Tester",
            "email": "inbox@example.com",
            "message": "Hello from contact API to verify admin inbox rendering.",
            "subject": "Inbox Test",
        },
    )
    assert sent.status_code == 201

    admin.post(
        "/api/auth/login",
        data={"email": "admin@example.com", "password": "admin123"},
    )

    inbox = admin.get("/admin/messages")
    assert inbox.status_code == 200
    assert "Messages" in inbox.text
    assert "Inbox Tester" in inbox.text
    assert "inbox@example.com" in inbox.text
    assert "Inbox Test" in inbox.text


def test_admin_comment_detail_modal_partial_renders(admin, blog):
    posts = blog.get("/api/posts")
    assert posts.status_code == 200
    slug = posts.json()[0]["slug"]

    created = blog.post(
        f"/api/comments/{slug}",
        json={
            "content": "Comment created for admin modal test.",
            "guest_name": "Modal Tester",
            "guest_email": "modal@example.com",
        },
    )
    assert created.status_code == 200

    admin.post(
        "/api/auth/login",
        data={"email": "admin@example.com", "password": "admin123"},
    )

    listing = admin.get("/admin/comments")
    assert listing.status_code == 200

    match = re.search(r'hx-get="/admin/comments/([0-9a-f-]{36})"', listing.text)
    assert match is not None

    detail = admin.get(f"/admin/comments/{match.group(1)}")
    assert detail.status_code == 200
    assert "Comment Details" in detail.text
    assert "Loading..." not in detail.text


def test_admin_settings_exposes_projects_source_mode(admin):
    admin.post(
        "/api/auth/login",
        data={"email": "admin@example.com", "password": "admin123"},
    )
    response = admin.get("/admin/settings")
    assert response.status_code == 200
    assert "Projects source mode" in response.text
    assert "Featured + automatic fallback" in response.text
    assert "Only featured projects" in response.text


def test_admin_analytics_sse_endpoint_exists(admin):
    assert any(getattr(route, "path", "") == "/events/admin.analytics" for route in admin.app.routes)
    response = admin.get("/events/admin.analytics", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/login"


def test_admin_logout(admin):
    admin.post(
        "/api/auth/login",
        data={"email": "admin@example.com", "password": "admin123"},
    )
    response = admin.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
