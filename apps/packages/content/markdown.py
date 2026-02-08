from __future__ import annotations

import markdown


def render_markdown(text: str) -> str:
    if not text:
        return ""
    return markdown.markdown(
        text,
        extensions=["fenced_code", "codehilite", "tables", "nl2br"],
    )
