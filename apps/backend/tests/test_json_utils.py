"""json_utils extraction."""

from __future__ import annotations

from app.pulse.json_utils import extract_json_object


def test_extract_plain_json() -> None:
    obj = extract_json_object('{"a": 1}')
    assert obj == {"a": 1}


def test_extract_fenced_json() -> None:
    text = """Here is JSON:\n```json\n{"x": "y"}\n```\n"""
    obj = extract_json_object(text)
    assert obj == {"x": "y"}
