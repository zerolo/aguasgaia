from dataclasses import dataclass
from typing import Any

@dataclass(init=True, repr=True)
class Consumption:
    consumption_value: float
    consumption_attributes: dict[str, Any]