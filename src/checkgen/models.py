from datetime import date, datetime
from decimal import Decimal

from num2words import num2words
from num2words.currency import parse_currency_parts


class Bank:
    def __init__(self, name: str, routing_number: str) -> None:
        self.name = name
        self.routing_number = routing_number


class Issuer:
    def __init__(self, name: str, details: str | None, bank: Bank, account_number: str) -> None:
        self.name = name
        self.details = details
        self.bank = bank
        self.account_number = account_number
        # , next_check_number: int = 1001
        # self._next_check_number = next_check_number

    # def get_next_check_number(self):
    #     current = self._next_check_number
    #
    #     self._next_check_number += 1
    #
    #     return current


class Payment:
    def __init__(self, payee: str, amount: float | Decimal, date: date | datetime, memo=None) -> None:
        self.payee = payee
        self._amount = amount
        self._date = date
        self.memo = memo

    @property
    def amount(self) -> str:
        return f"{self._amount:,.2f}"

    @property
    def date(self) -> str:
        return f"{self._date.month}/{self._date.day}/{self._date.year}"

    def written_amount(self) -> str:
        dollars, cents, _ = parse_currency_parts(self._amount, is_int_with_cents=False)

        dollars = num2words(dollars).replace(' and', '').replace(',', '').replace('-', ' ')

        cents = f"{cents:02}" if cents else "XX"

        return f"{dollars.capitalize()} and {cents}/100"
