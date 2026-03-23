"""INDmoney FAQ extraction (Source 1)."""

from __future__ import annotations

from app.fee.scrape import extract_indmoney_exit_load_faq


def test_extract_indmoney_faq_from_expected_paragraph() -> None:
    html = """
    <div>Frequently Asked Questions</div>
    <h3>What is the exit load of the fund?</h3>
    <p>The exit load is 0.25% if redeemed in 0-30 Days, 0.1% if redeemed in 30-90 Days.
    Exit load is a fee levied for exiting the fund earlier than a stipulated period, usually 1 year.</p>
    """
    out = extract_indmoney_exit_load_faq(html)
    assert out is not None
    assert "0.25%" in out
    assert "0.1%" in out
    assert "stipulated period" in out.lower()
