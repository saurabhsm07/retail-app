import threading
import time

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from domain.models.order_line import OrderLine
from service_layer.unit_of_work import ProductRepoUnitOfWork
from tests.conftest import get_random_batch_ref, get_random_sku, get_random_order_id, insert_batch_record, \
    insert_product_record


def get_allocated_batch_ref(session: Session, orderid, sku):
    [[order_line_id]] = session.execute(text('SELECT id FROM order_lines WHERE order_id=:orderid AND sku=:sku'),
                                        dict(orderid=orderid,
                                             sku=sku)
                                        )
    [[batch_ref]] = session.execute(
        text('SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id'
             ' WHERE order_line_id=:order_line_id'),
        dict(order_line_id=order_line_id)
    )
    return batch_ref


def test_uow_can_retrieve_a_product_and_allocate_an_order_line(session_factory):
    session = session_factory()
    test_batch_ref = get_random_batch_ref()
    test_sku = get_random_sku()
    test_order_id = get_random_order_id()

    insert_product_record(session, test_sku)
    insert_batch_record(session, test_batch_ref, test_sku, 100)

    with ProductRepoUnitOfWork(session_factory) as uow:
        product = uow.products.get(test_sku)
        product.allocate(OrderLine(order_id=test_order_id, sku=test_sku, quantity=5))
        uow.commit()

    batch_ref = get_allocated_batch_ref(session, test_order_id, test_sku)

    assert batch_ref == test_batch_ref


def try_line_allocation(session_factory, order_line, exceptions) -> None:
    try:
        with ProductRepoUnitOfWork(session_factory) as uow:
            product = uow.products.get(order_line.sku)
            product.allocate(order_line)
            time.sleep(3)
            uow.commit()

    except Exception as e:
        exceptions.append(str(e))
        raise e


@pytest.mark.skip("To be executed once postgres integration is completed")
def test_two_concurrent_allocation_update_requests_on_the_same_product_are_not_allowed(session_factory):
    session = session_factory()
    test_batch_ref = get_random_batch_ref()
    test_sku = get_random_sku()
    test_order_id_1 = get_random_order_id()
    test_order_id_2 = get_random_order_id()

    insert_product_record(session, test_sku)
    insert_batch_record(session, test_batch_ref, test_sku, 100)

    exceptions_list = []
    attempt_allocation_line_1 = lambda: try_line_allocation(session_factory, OrderLine(test_order_id_1, test_sku, 5),
                                                            exceptions_list)
    attempt_allocation_line_2 = lambda: try_line_allocation(session_factory, OrderLine(test_order_id_2, test_sku, 5),
                                                            exceptions_list)

    t1 = threading.Thread(target=attempt_allocation_line_1)
    t2 = threading.Thread(target=attempt_allocation_line_2)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    [product] = list(session.execute(text('SELECT sku, version from PRODUCTS where sku=:sku'), dict(sku=test_sku)))
    assert len(exceptions_list) > 0
    assert product.version == 1
