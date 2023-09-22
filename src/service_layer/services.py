from typing import List
from domain.models.batch import Batch
from domain.models.order_line import OrderLine
from domain.models.batch import allocate as allocate_line
from adapters.repository import AbstractRepository


class InvalidSkuException(Exception):
    pass


def is_valid_sku(sku, batches: List[Batch]):
    if sku in [batch.sku for batch in batches]:
        return True
    else:
        return False


def allocate(order_line: OrderLine, repository: AbstractRepository, session):
    if not is_valid_sku(order_line.sku, repository.list()):
        raise InvalidSkuException(f'Invalid sku : {order_line.sku}')

    else:
        batch_ref = allocate_line(order_line=order_line, batches=repository.list())
        session.commit()

        return batch_ref
