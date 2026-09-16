from datetime import date, time
from decimal import Decimal

import pytest

from banking_toolkit.transaction import DcIndicator, Transaction, TxnType

ACCOUNT = "ES7620770024003102575766"


def coffee() -> Transaction:
    """Movement A from the layout doc: 1.80 EUR card payment."""
    return Transaction(
        txn_id=1,
        account_iban=ACCOUNT,
        booking_date=date(2026, 9, 16),
        value_date=date(2026, 9, 16),
        booking_time=time(8, 30, 0),
        txn_type=TxnType.CARD,
        dc_indicator=DcIndicator.DEBIT,
        amount=Decimal("1.80"),
        description="Cafe Bar Manolo Madrid",
    )


def test_record_is_150_chars():
    assert len(coffee().to_record()) == 150


def test_amount_uses_implied_decimals():
    record = coffee().to_record()
    assert record[63:76] == "0000000000180"      # positions 64-76


def test_three_letter_type_is_padded_to_four():
    txn = Transaction(
        txn_id=2, account_iban=ACCOUNT,
        booking_date=date(2026, 9, 16), value_date=date(2026, 9, 16),
        booking_time=time(11, 5, 0),
        txn_type=TxnType.TRF, dc_indicator=DcIndicator.CREDIT,
        amount=Decimal("1250.00"),
        counterparty_iban="ES9121000418450200051332",
        description="Alquiler septiembre",
    )
    record = txn.to_record()
    assert record[58:62] == "TRF "               # positions 59-62
    assert record[79:103] == "ES9121000418450200051332"


def test_empty_counterparty_is_24_spaces():
    record = coffee().to_record()
    assert record[79:103] == " " * 24


def test_negative_amount_is_rejected():
    with pytest.raises(ValueError):
        Transaction(
            txn_id=3, account_iban=ACCOUNT,
            booking_date=date(2026, 9, 16), value_date=date(2026, 9, 16),
            booking_time=time(3, 0, 0),
            txn_type=TxnType.DDEB, dc_indicator=DcIndicator.DEBIT,
            amount=Decimal("-87.43"),
        )
