import pytest
from library_service import (
    get_patron_status_report
)


def test_patron_status_valid():
    report = get_patron_status_report("123456")

    assert isinstance(report, dict)
    assert "borrow_count" in report
    assert "currently_borrowed" in report
    assert "total_late_fees" in report


def test_patron_status_no_borrows():
    report = get_patron_status_report("654321")

    assert isinstance(report, dict)
    assert "borrow_count" in report
    assert report["borrow_count"] == 0
    assert "total_late_fees" in report


def test_patron_status_invalid_patron_id():
    report = get_patron_status_report("12A45A")

    assert isinstance(report, dict)
    assert "error" in report
    assert "invalid patron" in report["error"].lower()

