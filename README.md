# checkgen

Print checks on 3 checks per page in bulk.

## Installation

```shell
$ pip install checkgen
```

Sample usage

```python3
from datetime import datetime

from checkgen.models import Issuer, Bank
from checkgen.printer import Printer

issuer = Issuer('Samantha Johnson', '123 Main Street', Bank('Lakeside National Bank', '123456789'), '9876543210')
printer = Printer(issuer)
printer.distribute_payment('John Smith', 3000, 1200, datetime(2025, 1, 1), memo='Not a real check')

checks, _ = printer.print()

with open('checks.pdf', 'wb') as f:
    checks.to_file(f)
```

## Credits

Inspired and adapted from https://github.com/veterinarian/checkprint/
