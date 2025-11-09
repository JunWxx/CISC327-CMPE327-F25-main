import pytest
from unittest.mock import Mock
from services.payment_service import PaymentGateway
from services.library_service import refund_late_fee_payment

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


def test_refund_late_fee_payment_gateway_failure():
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (False, "Some gateway error")

    success, message = refund_late_fee_payment(
        transaction_id="txn_123456_12345678",
        amount=5.00,
        payment_gateway=gateway,
    )

    assert success is False
    assert message == "Refund failed: Some gateway error"
    gateway.refund_payment.assert_called_once_with("txn_123456_12345678", 5.00)


def test_refund_late_fee_payment_network_error_handled():
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.side_effect = RuntimeError("Network down")

    success, message = refund_late_fee_payment(
        transaction_id="txn_123456_12345678",
        amount=5.00,
        payment_gateway=gateway,
    )

    assert success is False
    assert message == "Refund processing error: Network down"
    gateway.refund_payment.assert_called_once_with("txn_123456_12345678", 5.00)