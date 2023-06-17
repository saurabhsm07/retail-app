from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Set

from models.order_line import OrderLine


@dataclass()
class Batch:
    id: int
    sku: str
    quantity: int
    eta: datetime
    _allocations: Set[OrderLine] = field(init=False, default_factory=set)

    def allocate(self, order_line: OrderLine):
        try:
            if self.can_allocate(order_line):
                self._allocations.add(order_line)
        except Exception as e:
            raise Exception('Order allocation failed: ' + str(e))

    def deallocate(self, order_line):
        if order_line in self._allocations:
            self._allocations.remove(order_line)
            return True

        return False

    def can_allocate(self, order_line: OrderLine) -> bool:
        if order_line.sku == self.sku and order_line.quantity <= self.available_quantity and order_line not in self._allocations:
            return True

        return False

    @property
    def available_quantity(self):
        return self.quantity - self.allocated_quantity

    @property
    def allocated_quantity(self):
        return sum(order_line.quantity for order_line in self._allocations)
