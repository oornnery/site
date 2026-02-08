from __future__ import annotations

import html
import re


def sanitize_html(text: str) -> str:
    if not text:
        return ""
    return html.escape(text)


def sanitize_slug(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9-]", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")
