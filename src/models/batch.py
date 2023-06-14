from dataclasses import dataclass
from datetime import datetime
from typing import List

from models.order_line import OrderLine


@dataclass()
class Batch:
    id: int
    sku: str
    available_quantity: int
    eta: datetime
    _allocations = set()

    def allocate(self, order_line: OrderLine):
        try:
            if self.can_allocate(order_line):
                self._allocations.add(order_line)
                self.available_quantity -= order_line.quantity
        except Exception as e:
            raise Exception('Order allocation failed: ' + str(e))

    def deallocate(self, order_line):
        if order_line in self._allocations:
            self._allocations.remove(order_line)
            self.available_quantity += order_line.quantity
            return True

        return False

    def can_allocate(self, order_line: OrderLine) -> bool:
        if order_line.sku == self.sku and order_line.quantity <= self.available_quantity and order_line not in self._allocations:
            return True

        return False

    def get_allocations(self):
        return self._allocations
