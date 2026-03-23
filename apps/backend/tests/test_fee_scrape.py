"""HTML strip helper for fee source pages."""

from __future__ import annotations

from app.fee.scrape import strip_html_to_text


def test_strip_html_removes_tags_and_scripts() -> None:
    html = """
    <html><head><script>alert(1)</script><style>.x{}</style></head>
    <body><p>Hello <b>world</b></p></body></html>
    """
    t = strip_html_to_text(html)
    assert "script" not in t.lower()
    assert "Hello" in t
    assert "world" in t
