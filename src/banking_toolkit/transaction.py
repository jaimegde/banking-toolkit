"""Transaction record: the 150-byte fixed-length layout in docs/transaction-record-layout.md."""

from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from enum import Enum

RECORD_LENGTH = 150
IBAN_LENGTH = 24
DESCRIPTION_LENGTH = 40
FILLER_LENGTH = 7


class TxnType(str, Enum):
    CARD = "CARD"
    ATM = "ATM"
    TRF = "TRF"
    DDEB = "DDEB"
    SAL = "SAL"
    FEE = "FEE"
    INT = "INT"


class DcIndicator(str, Enum):
    DEBIT = "D"
    CREDIT = "C"


@dataclass(frozen=True)
class Transaction:
    txn_id: int
    account_iban: str
    booking_date: date
    value_date: date
    booking_time: time
    txn_type: TxnType
    dc_indicator: DcIndicator
    amount: Decimal
    currency: str = "EUR"
    counterparty_iban: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        if len(self.account_iban) != IBAN_LENGTH:
            raise ValueError(f"account_iban must be {IBAN_LENGTH} chars: {self.account_iban!r}")
        if self.counterparty_iban and len(self.counterparty_iban) != IBAN_LENGTH:
            raise ValueError(f"counterparty_iban must be {IBAN_LENGTH} chars or empty")
        if self.amount < 0:
            raise ValueError("amount must be positive; direction goes in dc_indicator")
        if len(self.currency) != 3:
            raise ValueError(f"currency must be an ISO 4217 code: {self.currency!r}")

    def to_record(self) -> str:
        """Serialize to one 150-char fixed-length line (no newline)."""
        amount_cents = int(self.amount.quantize(Decimal("0.01")) * 100)
        record = (
            f"{self.txn_id:012d}"                                   # 1-12   N
            + self.account_iban                                     # 13-36  A
            + self.booking_date.strftime("%Y%m%d")                  # 37-44  N
            + self.value_date.strftime("%Y%m%d")                    # 45-52  N
            + self.booking_time.strftime("%H%M%S")                  # 53-58  N
            + self.txn_type.value.ljust(4)                          # 59-62  A
            + self.dc_indicator.value                               # 63     A
            + f"{amount_cents:013d}"                                # 64-76  N
            + self.currency                                         # 77-79  A
            + self.counterparty_iban.ljust(IBAN_LENGTH)             # 80-103 A
            + self.description.upper()[:DESCRIPTION_LENGTH].ljust(DESCRIPTION_LENGTH)  # 104-143 A
            + " " * FILLER_LENGTH                                   # 144-150 A
        )
        assert len(record) == RECORD_LENGTH, len(record)
        return record
