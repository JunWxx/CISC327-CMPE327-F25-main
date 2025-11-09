import pytest
from unittest.mock import Mock
from services.payment_service import PaymentGateway
from services.library_service import pay_late_fees
from services.library_service import refund_late_fee_payment

## 1.pay_late_fees_test

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

## 2.test_refund_late_dee_payment
def test_refund_late_fee_payment_success():
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (
        True,
        "Refund of $5.00 processed successfully."
    )

    success, message = refund_late_fee_payment(
        transaction_id="txn_123456_12345678",
        amount=5.00,
        payment_gateway=gateway,
    )

    assert success == True
    assert message == "Refund of $5.00 processed successfully."

    gateway.refund_payment.assert_called_once_with("txn_123456_12345678", 5.00)

def test_refund_late_fee_payment_invalid_transaction_id():
    gateway = Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment(
        transaction_id="invalid_txn_id",
        amount=5.00,
        payment_gateway=gateway,
    )

    assert success == False
    assert message == "Invalid transaction ID."

    gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_negative():
    gateway = Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment(
        transaction_id="txn_123456_12345678",
        amount=-1.0,
        payment_gateway=gateway,
    )

    assert success == False
    assert message == "Refund amount must be greater than 0."
    gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_zero():
    gateway = Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment(
        transaction_id="txn_123456_12345678",
        amount=0,
        payment_gateway=gateway,
    )

    assert success == False
    assert message == "Refund amount must be greater than 0."
    gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_exceeds():
    gateway = Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment(
        transaction_id="txn_123456_12345678",
        amount=20.0,
        payment_gateway=gateway,
    )

    assert success == False
    assert message == "Refund amount exceeds maximum late fee."
    gateway.refund_payment.assert_not_called()

##3. addtional test cases for 80% coverage- (test payment_service)

def test_process_payment_success(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)
    mocker.patch("services.payment_service.time.time", return_value=1234567890)

    gateway = PaymentGateway()
    success, txn_id, msg = gateway.process_payment("123456", 10.0, "Late fees")

    assert success == True
    assert txn_id == "txn_123456_1234567890"
    assert msg == "Payment of $10.00 processed successfully"


def test_process_payment_amount_zero(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)

    gateway = PaymentGateway()
    success, txn_id, msg = gateway.process_payment("123456", 0.0, "Late fees")

    assert success == False
    assert txn_id == ""
    assert msg == "Invalid amount: must be greater than 0"


def test_process_payment_exceeds(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)

    gateway = PaymentGateway()
    success, txn_id, msg = gateway.process_payment("123456", 1001.0, "Late fees")

    assert success == False
    assert txn_id == ""
    assert msg == "Payment declined: amount exceeds limit"


def test_process_payment_invalid_patron_id(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)

    gateway = PaymentGateway()
    success, txn_id, msg = gateway.process_payment("12345", 10.0, "Late fees")

    assert success == False
    assert txn_id == ""
    assert msg == "Invalid patron ID format"

def test_refund_payment_invalid_transaction_id(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)

    gateway = PaymentGateway()
    success, msg = gateway.refund_payment("bad_txn", 5.0)

    assert success == False
    assert msg == "Invalid transaction ID"


def test_refund_payment_invalid_amount(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)

    gateway = PaymentGateway()
    success, msg = gateway.refund_payment("txn_123456_1234567890", -1.0)

    assert success == False
    assert msg == "Invalid refund amount"
