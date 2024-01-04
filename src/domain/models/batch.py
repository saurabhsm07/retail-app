from datetime import datetime
from typing import List, Optional

from domain.models.order_line import OrderLine


class Batch:

    def __init__(self, reference: str,
                 sku: str,
                 quantity: int,
                 eta: Optional[datetime]):
        self.reference = reference
        self.sku = sku
        self.quantity = quantity
        self.eta = eta
        self._allocations = set()

    def allocate(self, order_line: OrderLine):
        try:
            if self.can_allocate(order_line):
                self._allocations.add(order_line)
        except Exception as e:
            raise Exception('Order allocation failed: ' + str(e))

    def deallocate(self, order_line: OrderLine):
        if order_line in self._allocations:
            self._allocations.remove(order_line)
            return True

        return False

    def can_allocate(self, order_line: OrderLine) -> bool:
        if (order_line.sku == self.sku and order_line.quantity <= self.available_quantity
                and order_line not in self._allocations):
            return True

        return False

    @property
    def available_quantity(self):
        return self.quantity - self.allocated_quantity

    @property
    def allocated_quantity(self):
        return sum(order_line.quantity for order_line in self._allocations)

    def __eq__(self, other):
        if isinstance(other, Batch):
            if self.reference == other.reference:
                return True
        return False

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta
