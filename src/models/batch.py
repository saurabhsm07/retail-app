from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Set, Tuple, Dict

from models.order_line import OrderLine


class OutOfStock(Exception):
    pass


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

    def __eq__(self, other):
        if isinstance(other, Batch):
            if self.id == other.id:
                return True
        return False

    def __hash__(self):
        return hash(self.id)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta


def allocate(order_line: OrderLine, batches: List[Batch]) -> Dict[str, int]:
    """
    method selects most suitable batch from a list of batches for a particular order line,
    raises OutOfStock exception if order cannot be fulfilled
    :param order_line:
    :param batches:
    :return: dict of order_id, batch_id (batch this particular order line is allocated to)
    """
    most_suitable_batch = None
    for batch in sorted(batches):
        if batch.can_allocate(order_line):
            most_suitable_batch = batch
            break

    if most_suitable_batch is not None:
        most_suitable_batch.allocate(order_line)
        return {'order_id': order_line.order_id, 'batch_id': most_suitable_batch.id}

    raise OutOfStock(f'Product {order_line.sku} of quantity {order_line.quantity} unavailable')
