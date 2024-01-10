import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from domain.models.order_line import OrderLine
from domain.models.product import allocate as allocate_line
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
        allocate_line(OrderLine(order_id=test_order_id, sku=test_sku, quantity=5), product)
        uow.commit()

    batch_ref = get_allocated_batch_ref(session, test_order_id, test_sku)

    assert batch_ref == test_batch_ref
