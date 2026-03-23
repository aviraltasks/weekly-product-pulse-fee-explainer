"""Weekly Pulse N counter persistence."""

from __future__ import annotations

from app.preview.counter import increment_weekly_pulse_n, read_last_n


def test_counter_increments_sequentially(tmp_path) -> None:
    p = tmp_path / "c.json"
    assert read_last_n(p) == 0
    assert increment_weekly_pulse_n(p) == 1
    assert increment_weekly_pulse_n(p) == 2
    assert read_last_n(p) == 2
