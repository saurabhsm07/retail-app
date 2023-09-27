from typing import List
from domain.models.batch import Batch
from domain.models.order_line import OrderLine
from domain.models.batch import allocate as allocate_line
from adapters.repository import AbstractRepository

'''
UPDATES:
    -   Service layer deallocate method requires 2 repositories as input (order line, batch) to execute successfully
'''


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


def deallocate(order_id: str, batch_ref: str, batch_repository: AbstractRepository, order_line_repo: AbstractRepository,
               session):
    '''
    :param order_id:
    :param batch_ref:
    :param batch_repository: batch repository object to fetch necessary batch from DB
    :param order_line_repo: order line repository object to fetch order line data from DB
    :param session:
    :return:
    '''

    try:

        batch = batch_repository.get(batch_ref)
        order_line = order_line_repo.get_by_order_id_and_sku(order_id, batch.sku)
        status = batch.deallocate(order_line)

        session.commit()

        return status, order_line.quantity

    except Exception as e:
        raise e
