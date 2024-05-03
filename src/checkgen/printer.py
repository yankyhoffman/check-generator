import enum
import math
from datetime import datetime, timedelta

from checkgen.models import Payment
from checkgen.document import Check, Document


class Period(enum.Enum):
    WEEKLY = enum.auto()
    BIWEEKLY = enum.auto()
    MONTHLY = enum.auto()

    def increment(self, date):
        if self is self.MONTHLY:
            month = date.month + 1 if date.month < 12 else 1
            year = date.year + 1 if month == 1 else date.year

            return datetime(year, month, date.day)

        if self is self.WEEKLY:
            return date + timedelta(days=7)

        if self is self.BIWEEKLY:
            return date + timedelta(days=14)


class EmptyChecks(enum.Enum):
    PRINT = enum.auto()
    BLANK = enum.auto()


class PrintType(enum.Flag):
    NONE = enum.auto()
    MICR = enum.auto()
    LABELS = enum.auto()
    INFORMATION = enum.auto()


class Printer:
    def __init__(self, issuer, starting_check_number=1001):
        self.issuer = issuer
        self.starting_check_number = starting_check_number

        self._payments = []

    def add_payments(self, payee, check_amount, start_date, memo=None, *, count=1, payment_period=Period.MONTHLY):
        date = start_date

        for _ in range(count):
            self._payments.append(Payment(payee, check_amount, date, memo))

            date = payment_period.increment(date)

    def distribute_payment(self, payee, total_amount, check_amount, start_date, memo=None,
                           *, payment_period=Period.MONTHLY, fold_last_payment=False):
        payments, remainder = divmod(total_amount, check_amount)

        date = start_date

        for _ in range(payments):
            self._payments.append(Payment(payee, check_amount, date, memo))

            date = payment_period.increment(date)

        if remainder:
            if fold_last_payment and payments:
                self._payments[-1].amount += remainder
            else:
                self._payments.append(Payment(payee, remainder, date, memo))

    def print(self, *, empty_checks=EmptyChecks.PRINT, type=PrintType.MICR | PrintType.LABELS | PrintType.INFORMATION,
              target_num_checks=0):
        num_checks = math.ceil(max(len(self._payments), target_num_checks) / 3) * 3 \
            if empty_checks is EmptyChecks.PRINT \
            else len(self._payments)

        book = Book(self.issuer, max(num_checks, target_num_checks), self.starting_check_number)

        report = book.print(self._payments, type=type)

        return book, report


class Book:
    def __init__(self, issuer, num_checks=3, starting_check_number=1001):
        self.document = Document()

        self.checks = []
        for i in range(num_checks):
            self.checks.append(Check(issuer, starting_check_number + i))

    def print(self, payments=None, *, type=PrintType.MICR | PrintType.LABELS | PrintType.INFORMATION):
        report = []

        for i, check in enumerate(self.checks):
            record = {'num': check.check_number, 'date': None, 'payee': None, 'amount': None}

            if i % 3 == 0:
                self.document.add_page()

            self.document.set_offset(i % 3)

            if PrintType.MICR in type:
                check.print_micr(self.document)

            if PrintType.LABELS in type:
                check.print_check_labels(self.document)

            if PrintType.INFORMATION in type:
                check.print_check_information(self.document)

            if payments and i < len(payments):
                payment = payments[i]

                record |= {'date': payment.date, 'payee': payment.payee, 'amount': payment.amount}

                check.fill_check(self.document, payment)

            report.append(record)

        return report

    def to_file(self, handle):
        handle.write(self.document.output())
