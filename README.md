# checkprint

Print checks on 3 checks per page in bulk.

Sample usage

```python
from datetime import datetime

from checkprint.models import Issuer, Bank
from checkprint.printer import Printer

issuer = Issuer('Samantha Johnson', '123 Main Street', Bank('Lakeside National Bank', '123456789'), '98765432101')
printer = Printer(issuer)
printer.distribute_payment('John Smith', 3000, 1200, datetime(2025, 1, 1), memo='Not a real check')

checks, _ = printer.print()

with open('checks.pdf', 'wb') as f:
    checks.to_file(f)
```

## Credits

Inspired and adapted from https://github.com/veterinarian/checkprint/
