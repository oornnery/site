from __future__ import annotations

from datetime import datetime, timezone
from xml.sax.saxutils import escape


def build_rss(*, title: str, link: str, description: str, items: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0">',
        "<channel>",
        f"<title>{escape(title)}</title>",
        f"<link>{escape(link)}</link>",
        f"<description>{escape(description)}</description>",
        f"<lastBuildDate>{now}</lastBuildDate>",
    ]
    for item in items:
        lines.extend(
            [
                "<item>",
                f"<title>{escape(str(item.get('title', '')))}</title>",
                f"<link>{escape(str(item.get('link', '')))}</link>",
                f"<description>{escape(str(item.get('description', '')))}</description>",
                "</item>",
            ]
        )
    lines.extend(["</channel>", "</rss>"])
    return "\n".join(lines)
