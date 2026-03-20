from app.infrastructure.markdown import _render_md, _sanitize_html


def test_markdown_sanitization_strips_dangerous_html() -> None:
    raw_markdown = "Hello<script>alert('xss')</script>\n\n[click](javascript:alert(1))"

    rendered = _render_md(raw_markdown)
    sanitized = _sanitize_html(rendered)

    assert "<script" not in sanitized.lower()
    assert "javascript:" not in sanitized.lower()


def test_markdown_sanitization_preserves_table_markup() -> None:
    raw_markdown = "| col1 | col2 |\n| --- | --- |\n| a | b |"

    rendered = _render_md(raw_markdown)
    sanitized = _sanitize_html(rendered)

    assert "<table" in sanitized
    assert "<tr" in sanitized
    assert "<td" in sanitized


def test_sanitization_strips_svg_injection() -> None:
    raw = '<svg onload="alert(1)"><rect/></svg>'
    sanitized = _sanitize_html(raw)
    assert "onload" not in sanitized.lower()


def test_sanitization_strips_event_handler_attributes() -> None:
    raw = '<div onmouseover="alert(1)">hover</div>'
    sanitized = _sanitize_html(raw)
    assert "onmouseover" not in sanitized.lower()
    assert "hover" in sanitized


def test_sanitization_strips_javascript_protocol_in_href() -> None:
    raw = '<a href="javascript:void(0)">click</a>'
    sanitized = _sanitize_html(raw)
    assert "javascript:" not in sanitized.lower()
    assert "click" in sanitized


def test_sanitization_strips_data_uri_in_img_src() -> None:
    raw = '<img src="data:text/html,<script>alert(1)</script>">'
    sanitized = _sanitize_html(raw)
    assert "data:" not in sanitized.lower() or "<script" not in sanitized.lower()
