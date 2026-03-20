import logging
import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.models.models import BlogComment

logger = logging.getLogger(__name__)
_GIST_ID_PATTERN = re.compile(r"^[0-9a-fA-F]{8,40}$")


def _extract_gist_id(gist_url: str) -> str:
    raw = gist_url.strip()
    if not raw:
        return ""

    if _GIST_ID_PATTERN.fullmatch(raw):
        return raw.lower()

    try:
        parsed = urlparse(raw)
    except ValueError:
        return ""

    host = parsed.netloc.lower()
    if host not in {"gist.github.com", "www.gist.github.com"}:
        return ""

    path_parts = [part for part in parsed.path.split("/") if part]
    if not path_parts:
        return ""

    candidate = path_parts[-1]
    if candidate.lower() == "raw" and len(path_parts) > 1:
        candidate = path_parts[-2]

    if _GIST_ID_PATTERN.fullmatch(candidate):
        return candidate.lower()
    return ""


def _github_api_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "site-app",
    }
    token = settings.github_token.strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch_gist_payload(gist_id: str) -> dict[str, Any] | None:
    if not gist_id:
        return None

    url = f"https://api.github.com/gists/{gist_id}"
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=float(settings.github_api_timeout_seconds),
        ) as client:
            response = client.get(url, headers=_github_api_headers())
        if response.status_code == 404:
            logger.warning(f"Gist not found for gist_id={gist_id}.")
            return None
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            return payload
    except (httpx.HTTPError, ValueError):
        logger.exception(f"Failed to fetch gist payload for gist_id={gist_id}.")
    return None


def _fetch_gist_raw_content(raw_url: str) -> str:
    if not raw_url:
        return ""
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=float(settings.github_api_timeout_seconds),
        ) as client:
            response = client.get(raw_url, headers={"User-Agent": "site-app"})
        response.raise_for_status()
        return response.text.strip()
    except httpx.HTTPError:
        logger.exception(f"Failed to fetch gist raw content from raw_url={raw_url}.")
        return ""


def _pick_gist_file(
    files: dict[str, Any], file_hint: str = ""
) -> dict[str, Any] | None:
    if not files:
        return None

    hint = file_hint.strip()
    if hint:
        if hint in files and isinstance(files[hint], dict):
            return files[hint]
        lower_hint = hint.lower()
        for filename, file_data in files.items():
            if filename.lower() == lower_hint and isinstance(file_data, dict):
                return file_data

    for filename, file_data in files.items():
        if filename.lower().endswith(".md") and isinstance(file_data, dict):
            return file_data

    for file_data in files.values():
        if isinstance(file_data, dict):
            return file_data
    return None


def _extract_gist_markdown(gist_payload: dict[str, Any], file_hint: str = "") -> str:
    files = gist_payload.get("files")
    if not isinstance(files, dict):
        return ""

    selected = _pick_gist_file(files, file_hint)
    if selected is None:
        return ""

    content = selected.get("content")
    truncated = bool(selected.get("truncated"))
    if isinstance(content, str) and content.strip() and not truncated:
        return content.strip()

    raw_url = str(selected.get("raw_url") or "").strip()
    if raw_url:
        return _fetch_gist_raw_content(raw_url)

    if isinstance(content, str):
        return content.strip()
    return ""


def _format_github_timestamp(raw: str) -> str:
    if not raw:
        return ""
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return parsed.strftime("%b %d, %Y")
    except ValueError:
        return raw


def _gist_comments_url(gist_url: str) -> str:
    url = gist_url.strip()
    if not url:
        return ""
    if "#comments" in url:
        return url
    return f"{url}#comments"


def _fetch_gist_comments(gist_id: str) -> tuple[BlogComment, ...]:
    if not gist_id:
        return ()

    url = f"https://api.github.com/gists/{gist_id}/comments"
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=float(settings.github_api_timeout_seconds),
        ) as client:
            response = client.get(
                url,
                headers=_github_api_headers(),
                params={"per_page": str(settings.github_gist_comments_limit)},
            )
        if response.status_code == 404:
            logger.warning(f"Gist comments not found for gist_id={gist_id}.")
            return ()
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            return ()

        comments: list[BlogComment] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            user = item.get("user")
            user_data = user if isinstance(user, dict) else {}
            body = str(item.get("body") or "").strip()
            if not body:
                continue

            comments.append(
                BlogComment(
                    author=str(user_data.get("login") or "GitHub user"),
                    body=body,
                    created_at=_format_github_timestamp(
                        str(item.get("created_at") or "")
                    ),
                    profile_url=str(user_data.get("html_url") or "").strip(),
                    html_url=str(item.get("html_url") or "").strip(),
                    avatar_url=str(user_data.get("avatar_url") or "").strip(),
                )
            )

        return tuple(comments)
    except (httpx.HTTPError, ValueError):
        logger.exception(f"Failed to fetch gist comments for gist_id={gist_id}.")
        return ()
