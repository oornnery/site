from __future__ import annotations

import re
from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.main import create_app
from app.infrastructure.markdown import load_all_blog_posts, load_all_projects


def _extract_csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match is not None
    return match.group(1)


def _build_client() -> Iterator[TestClient]:
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_public_routes_return_success_status() -> None:
    for client in _build_client():
        for path in (
            "/",
            "/about",
            "/projects",
            "/contact",
            "/blog",
            "/blog/posts",
            "/blog/tags",
            "/blog/feed.xml",
        ):
            response = client.get(path)
            assert response.status_code == 200


def test_base_layout_includes_favicon() -> None:
    for client in _build_client():
        response = client.get("/")
        assert response.status_code == 200
        assert (
            'rel="icon" type="image/svg+xml" href="/static/favicon.svg"'
            in response.text
        )


def test_project_detail_existing_and_missing_slug() -> None:
    projects = load_all_projects()
    assert projects
    existing_slug = projects[0].slug

    for client in _build_client():
        ok_response = client.get(f"/projects/{existing_slug}")
        missing_response = client.get("/projects/slug-that-does-not-exist")
        assert ok_response.status_code == 200
        assert missing_response.status_code == 404


def test_blog_post_detail_existing_and_missing_slug() -> None:
    posts = load_all_blog_posts()
    assert posts
    existing_slug = posts[0].slug

    for client in _build_client():
        ok_response = client.get(f"/blog/posts/{existing_slug}")
        missing_response = client.get("/blog/posts/slug-that-does-not-exist")
        assert ok_response.status_code == 200
        assert missing_response.status_code == 404


def test_blog_tag_detail_route_returns_success() -> None:
    posts = load_all_blog_posts()
    assert posts
    first_tag = posts[0].tags[0]

    for client in _build_client():
        response = client.get(f"/blog/tags/{first_tag}")
        assert response.status_code == 200


def test_resume_download_returns_markdown_file() -> None:
    for client in _build_client():
        response = client.get("/about/resume.md")
        assert response.status_code == 200
        assert "text/markdown" in response.headers["content-type"]
        assert response.headers.get("content-disposition", "").startswith("attachment")


def test_blog_feed_returns_rss_xml() -> None:
    for client in _build_client():
        response = client.get("/blog/feed.xml")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/rss+xml")
        assert "<rss" in response.text
        assert "<channel>" in response.text


def test_contact_submission_success_flow() -> None:
    for client in _build_client():
        get_response = client.get("/contact", headers={"user-agent": "pytest-agent"})
        csrf_token = _extract_csrf_token(get_response.text)

        post_response = client.post(
            "/contact",
            data={
                "name": "Alice Example",
                "email": "alice@example.com",
                "subject": "Portfolio Contact",
                "message": "Hello, I would like to discuss a project collaboration.",
                "csrf_token": csrf_token,
            },
            headers={"user-agent": "pytest-agent"},
        )

        assert post_response.status_code == 200
        assert "Message sent successfully" in post_response.text


def test_contact_submission_rejects_invalid_csrf() -> None:
    for client in _build_client():
        post_response = client.post(
            "/contact",
            data={
                "name": "Alice Example",
                "email": "alice@example.com",
                "subject": "Portfolio Contact",
                "message": "Hello, I would like to discuss a project collaboration.",
                "csrf_token": "invalid-token",
            },
            headers={"user-agent": "pytest-agent"},
        )

        assert post_response.status_code == 403
        assert "Invalid or expired security token" in post_response.text


def test_contact_submission_returns_validation_errors() -> None:
    for client in _build_client():
        get_response = client.get("/contact", headers={"user-agent": "pytest-agent"})
        csrf_token = _extract_csrf_token(get_response.text)

        post_response = client.post(
            "/contact",
            data={
                "name": "A",
                "email": "not-an-email",
                "subject": "Hi",
                "message": "short",
                "csrf_token": csrf_token,
            },
            headers={"user-agent": "pytest-agent"},
        )

        assert post_response.status_code == 422
        assert "valid email address" in post_response.text
