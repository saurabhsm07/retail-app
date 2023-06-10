from dataclasses import dataclass
from datetime import datetime

from models.order_line import OrderLine


@dataclass()
class Batch:
    id: int
    sku: str
    available_quantity: int
    eta: datetime

    def allocate(self, order_line: OrderLine):
        try:
            if self.can_allocate(order_line):
                self.available_quantity -= order_line.quantity
        except Exception as e:
            raise Exception('Order allocation failed: ' + str(e))

    def can_allocate(self, order_line: OrderLine) -> bool:
        if order_line.sku == self.sku and order_line.quantity <= self.available_quantity:
            return True

        return False
