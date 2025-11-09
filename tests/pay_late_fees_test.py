import pytest
from unittest.mock import Mock
from services.payment_service import PaymentGateway
from services.library_service import pay_late_fees


def test_pay_late_fees_success(mocker):
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 27, "title": "1984", "available_copies": 1},
    )
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 4.50, "days_overdue": 3, "status": "Overdue"},
    )

    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (
        True,
        "txn_123456_100000",
        "Payment of $4.50 processed successfully",
    )

    success, message, txn_id = pay_late_fees("123456", 27, gateway)

    assert success is True
    assert "Payment successful!" in message
    assert "Payment of $4.50 processed successfully" in message
    assert txn_id == "txn_123456_100000"

    gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=4.50,
        description="Late fees for '1984'",
    )


def test_pay_late_fees_gateway_declined(mocker):
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 37, "title": "ABCD"},
    )
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 12.00, "days_overdue": 5, "status": "Overdue"},
    )

    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (
        False,
        "",
        "Payment failed",
    )

    success, message, txn_id = pay_late_fees("123456", 37, gateway)

    assert success is False
    assert message == "Payment failed: Payment failed"
    assert txn_id is None

    gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=12.00,
        description="Late fees for 'ABCD'",
    )


def test_pay_late_fees_invalid_patron_id(mocker):
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 47, "title": "Refactoring"},
    )
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 5.00, "days_overdue": 2, "status": "Overdue"},
    )

    gateway = Mock(spec=PaymentGateway)

    success, message, txn_id = pay_late_fees("BADID", 9, gateway)

    assert success is False
    assert message == "Invalid patron ID. Must be exactly 6 digits."
    assert txn_id is None
    gateway.process_payment.assert_not_called()


def test_pay_late_fees_zero_fee(mocker):
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 0.0, "days_overdue": 0, "status": "OnTime"},
    )
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 57, "title": "DCBA"},
    )

    gateway = Mock(spec=PaymentGateway)

    success, message, txn_id = pay_late_fees("123456", 57, gateway)

    assert success is False
    assert message == "No late fees to pay for this book."
    assert txn_id is None
    gateway.process_payment.assert_not_called()


def test_pay_late_fees_network_error(mocker):
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 3.25, "days_overdue": 1, "status": "Overdue"},
    )
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 67, "title": "ABCDE"},
    )

    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.side_effect = RuntimeError("Network Error")

    success, message, txn_id = pay_late_fees("123456", 67, gateway)

    assert success is False
    assert message == "Payment processing error: Network Error"
    assert txn_id is None

    gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=3.25,
        description="Late fees for 'ABCDE'",
    )


def test_pay_late_fees_fee_info_missing(mocker):
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value=None,  
    )
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 10, "title": "Dummy"},
    )

    gateway = Mock(spec=PaymentGateway)

    success, message, txn_id = pay_late_fees("123456", 10, gateway)

    assert success is False
    assert message == "Unable to calculate late fees."
    assert txn_id is None
    gateway.process_payment.assert_not_called()

def test_pay_late_fees_book_not_found(mocker):
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 3.0, "days_overdue": 2, "status": "Overdue"},
    )
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value=None,  
    )

    gateway = Mock(spec=PaymentGateway)

    success, message, txn_id = pay_late_fees("123456", 999, gateway)

    assert success is False
    assert message == "Book not found."
    assert txn_id is None
    gateway.process_payment.assert_not_called()