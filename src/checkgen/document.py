from contextlib import contextmanager

import fpdf
from pathlib import Path

FONTS = Path(__file__).absolute().parent / 'assets' / 'fonts'


class Document(fpdf.FPDF):
    def __init__(self):
        super().__init__(unit='in', format='Letter')

        # track check offset
        self._offset = 0

        self.set_margin(0)

        # add fonts
        self.add_font('regular', style='', fname=str(FONTS / 'OpenSans-Regular.ttf'))
        self.add_font('handwriting', style='', fname=str(FONTS / 'Cookie-Regular.ttf'))
        self.add_font('check', style='', fname=str(FONTS / 'micrenc.ttf'))
        self.add_font('metadata', style='', fname=str(FONTS / 'TitilliumWeb-Regular.ttf'))

        # define line style
        self.set_line_width(0.001)
        self.set_draw_color(r=48, g=48, b=48)

    def use_regular_font(self, size=0):
        self.set_font('regular', size=size)

    def use_handwriting_font(self, size=0):
        self.set_font('handwriting', size=size)

    def use_check_font(self, size=0):
        self.set_font('check', size=size)

    def use_metadata_font(self, size=0):
        self.set_font('metadata', size=size)

    def print_cell(self, value, *, width, height, pad=False, align=fpdf.Align.L):
        padding = '-'

        value_width = self.get_string_width(value)

        if value_width > width:
            self.set_stretching(100.0 * width / value_width)

        if pad and width > value_width:
            padding_width = self.get_string_width(padding)
            pad_length = int((width - value_width) / padding_width)
            value = f"{value} {padding * pad_length}"

        self.cell(width, height, value, align=align)
        self.set_stretching(100.0)

    def set_offset(self, offset):
        self._offset = offset * (11 / 3)

    def set_position(self, left, top):
        super().set_xy(x=left, y=top + self._offset)

    def horizontal_line(self, *, left, top, width):
        y = top + self._offset
        self.line(x1=left, x2=left + width, y1=y, y2=y)

    def vertical_line(self, *, left, top, height):
        y = top + self._offset
        self.line(y1=y, y2=y + height, x1=left, x2=left)

    def box(self, *, left, top, width, height):
        self.horizontal_line(left=left, top=top, width=width)
        self.horizontal_line(left=left, top=top + height, width=width)
        self.vertical_line(left=left, top=top, height=height)
        self.vertical_line(left=left + width, top=top, height=height)

    @contextmanager
    def use_rotation(self, angle, *, left, top):
        with self.rotation(angle, x=left, y=top + self._offset):
            yield


class Check:
    def __init__(self, issuer, check_number):
        self.issuer = issuer
        self.check_number = check_number

    def print_micr(self, document):
        value = f"c{self.check_number:06}c a{self.issuer.bank.routing_number}a {self.issuer.account_number}c"

        document.set_position(left=1.3, top=3)
        document.use_check_font(18)
        document.print_cell(value, width=7, height=0.25)

    @staticmethod
    def print_check_labels(document):
        # date
        document.horizontal_line(left=6.875, top=1, width=1)
        document.set_position(left=6.5, top=0.75)
        document.use_handwriting_font(12)
        document.print_cell('Date', width=0.5, height=0.25)

        # payee
        document.set_position(left=0.375, top=1.1)
        document.use_handwriting_font(10)
        document.print_cell('Pay to the', width=0.85, height=0.25)

        document.set_position(left=0.375, top=1.25)
        document.print_cell('order of', width=0.85, height=0.25)

        document.horizontal_line(left=0.875, top=1.45, width=5.625)
        document.vertical_line(left=6.5, top=1.25, height=0.2)

        # numeric amount
        document.set_position(left=6.6, top=1.2)
        document.use_handwriting_font(13)
        document.print_cell('$', width=0.15, height=0.25)

        document.box(left=6.75, top=1.2, width=1.1, height=0.25)

        # written amount
        document.set_position(left=7.05, top=1.55)
        document.use_handwriting_font(15)
        document.print_cell('Dollars', width=1, height=0.25)

        document.horizontal_line(left=0.375, top=1.825, width=6.675)

        # memo
        document.horizontal_line(left=0.65, top=2.52, width=2.35)
        document.set_position(left=1.3, top=2.5)
        document.use_handwriting_font(10)
        document.print_cell('Memo', width=1, height=0.25)

        # signature
        document.horizontal_line(left=5.15, top=2.52, width=2.35)
        document.set_position(left=5.8, top=2.5)
        document.use_handwriting_font(10)
        document.print_cell('Authorized Signature', width=1, height=0.25)

    def print_check_information(self, document):
        # payer
        document.set_position(left=0.6, top=0.25)
        document.use_metadata_font(16)
        document.print_cell(self.issuer.name, width=2.8, height=0.25, align=fpdf.Align.C)
        document.set_position(left=0.6, top=0.5)
        document.use_metadata_font(11)
        document.print_cell(self.issuer.details, width=2.8, height=0.25, align=fpdf.Align.C)

        # bank
        document.set_position(left=4, top=0.275)
        document.use_metadata_font(13)
        document.print_cell(self.issuer.bank.name, width=2, height=0.25, align=fpdf.Align.C)

        # check number
        document.set_position(left=7, top=0.25)
        document.use_regular_font(12)
        document.print_cell(str(self.check_number), width=1, height=0.25)

    def fill_check(self, document, payment):
        # payee
        document.set_position(left=0.875, top=1.2)
        document.use_regular_font(12)
        document.print_cell(payment.payee, width=5.5, height=0.25)

        # date
        document.set_position(left=6.875, top=0.75)
        document.use_regular_font(12)
        document.print_cell(payment.date, width=1.125, height=0.25)

        # numeric amount
        document.set_position(left=6.875, top=1.2)
        document.use_regular_font(12)
        document.print_cell(payment.amount, width=1.125, height=0.25)

        # written amount
        document.set_position(left=0.375, top=1.575)
        document.use_regular_font(12)
        document.print_cell(payment.written_amount(), width=6.6, height=0.25, pad=True)

        # memo
        if payment.memo:
            document.set_position(left=0.875, top=2.3)
            document.use_regular_font(10)
            document.print_cell(payment.memo, width=2, height=0.25)

    def mark_as_void(self, document):
        top = 2
        for left in [2, 4]:
            with document.use_rotation(45, left=left, top=top):
                document.set_position(left=left, top=top)
                document.use_metadata_font(20)
                document.print_cell('VOID VOID VOID', width=3, height=0.5)
