from typing import List

from domain.models.batch import Batch
from domain.models.order_line import OrderLine


class OutOfStockException(Exception):
    pass


class Product:
    def __init__(self, sku: str, batches: List[Batch], version: int = 0):
        self.sku = sku
        self.batches = batches
        self.version = version


def allocate(order_line: OrderLine, product: Product) -> str:
    """
    method selects most suitable batch from a list of product batches for a particular order line,
    raises OutOfStock exception if order cannot be fulfilled
    :param order_line:
    :param product: product that matches a particular SKU
    :return: batch_ref (batch this particular order line is allocated to)
    """
    batches = product.batches
    most_suitable_batch = None
    for batch in sorted(batches):
        if batch.can_allocate(order_line):
            most_suitable_batch = batch
            break

    if most_suitable_batch is not None:
        most_suitable_batch.allocate(order_line)
        return most_suitable_batch.reference

    raise OutOfStockException(f'Product {order_line.sku} of quantity {order_line.quantity} unavailable')
