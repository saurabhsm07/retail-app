from dataclasses import dataclass


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    quantity: int

    def __eq__(self, other):
        if isinstance(other, OrderLine):
            return True if self.order_id == other.order_id else False
        return False
