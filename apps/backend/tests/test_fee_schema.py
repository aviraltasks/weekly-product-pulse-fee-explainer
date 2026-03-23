"""FeeExplainerBlock validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.fee.schemas import FeeExplainerBlock


def test_fee_block_caps_bullets_at_six() -> None:
    b = FeeExplainerBlock(
        fee_scenario="Test",
        explanation_bullets=[f"b{i}" for i in range(10)],
        source_links=["https://a.example", "https://b.example"],
        last_checked_iso="2025-01-01T00:00:00Z",
    )
    assert len(b.explanation_bullets) == 6


def test_fee_block_requires_two_links() -> None:
    with pytest.raises(ValidationError):
        FeeExplainerBlock(
            fee_scenario="Test",
            explanation_bullets=["one"],
            source_links=["https://a.example"],
            last_checked_iso="2025-01-01T00:00:00Z",
        )
