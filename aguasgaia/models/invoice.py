from dataclasses import dataclass
from typing import Any

@dataclass(init=True, repr=True)
class Invoice:
    invoice_value: float
    invoice_attributes: dict[str, Any]