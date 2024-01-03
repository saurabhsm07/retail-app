from typing import List, Optional
from datetime import date
from domain.models.batch import Batch
from domain.models.order_line import OrderLine
from domain.models.batch import allocate as allocate_line
from adapters.repository import AbstractRepository
from service_layer.unit_of_work import AbstractBatchUnitOfWork

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


def insert_batch(batch_aow: AbstractBatchUnitOfWork, reference: str, sku: str, quantity: int, eta: Optional[date]):
    '''
    :param batch_aow: batch unit  of work object
    :param reference:
    :param sku:
    :param quantity:
    :param eta:
    :return: boolean True: inserted, False : didn't insert
    '''
    try:
        with batch_aow:
            batch_aow.batches.add(Batch(reference=reference, sku=sku, quantity=quantity, eta=eta))
            batch_aow.commit()

        return True

    except Exception as e:
        print("Error :" + e)
        print("str ERROR:" + str(e))


def allocate(order_line: OrderLine, repository: AbstractRepository, session):
    """
    Service layer method to allocate a valid order line to a particular batch
    :param order_line:
    :param repository: batch repository object
    :param session: database session object
    :return:
    """
    if not is_valid_sku(order_line.sku, repository.list()):
        raise InvalidSkuException(f'Invalid sku : {order_line.sku}')

    else:
        batch_ref = allocate_line(order_line=order_line, batches=repository.list())
        session.commit()

        return batch_ref


def deallocate(order_id: str, batch_ref: str, batch_repository: AbstractRepository, order_line_repo: AbstractRepository,
               session):
    '''
    deallocate method to remove an allocated line from a batch
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
