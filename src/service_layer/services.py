from typing import List, Optional
from datetime import date
from domain.models.batch import Batch
from domain.models.order_line import OrderLine
from domain.models.product import Product
from adapters.repository import AbstractRepository
from service_layer.unit_of_work import AbstractUnitOfWork

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


def insert_batch(product_uow: AbstractUnitOfWork, reference: str, sku: str, quantity: int, eta: Optional[date]):
    """
    :param product_uow: product unit of work object
    :param reference: batch unique reference
    :param sku: stock keeping unit of this batch
    :param quantity: quantity in this batch
    :param eta: time this batch will be delivered to the warehouse
    :return: boolean True: inserted, False : didn't insert
    """
    try:
        batch_obj = Batch(reference, sku, quantity, eta)
        with product_uow:
            product = product_uow.products.get(sku)
            if product:
                product.batches.append(batch_obj)
            else:
                product_uow.products.add(Product(sku, [batch_obj]))

            product_uow.commit()

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
    product = repository.get(order_line.sku)

    if not product:
        raise InvalidSkuException(f'Invalid sku : {order_line.sku}')
    else:
        batch_ref = product.allocate(order_line=order_line)
        session.commit()

    return batch_ref


def deallocate(batch_ref: str,
               order_line: OrderLine,
               product_repository: AbstractRepository,
               session):
    """
    deallocate method to remove an allocated line from a batch
    :param batch_ref:
    :param order_line:
    :param product_repository: product repository object to fetch necessary batch from DB
    :param session:
    :return: status of de-allocation request
    """

    try:

        batch = next(batch for batch in product_repository.get(order_line.sku).batches if batch.reference == batch_ref)
        status = batch.deallocate(order_line)

        session.commit()

        return status

    except Exception as e:
        raise e
