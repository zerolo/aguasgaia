from dataclasses import dataclass
from typing import Any


@dataclass(repr=True)
class Subscription:
    subscription_id: str
    active: bool
    address: str
    activation_date: str

    def __init__(self, subscription_payload):
        self.subscription_id = subscription_payload.get("subscriptionId", None)
        self.address = subscription_payload.get("clientAddress", None)
        self.activation_date = subscription_payload.get("activationDate", None)
        self.active = subscription_payload.get("isActive", False)
