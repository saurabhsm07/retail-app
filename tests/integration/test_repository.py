import pytest
from sqlalchemy import text

from adapters.repository import ProductRepository
from domain.models.batch import Batch
from domain.models.order_line import OrderLine
from datetime import datetime, timedelta

from domain.models.product import Product
from tests.conftest import get_random_sku, get_random_batch_ref, insert_product_record, insert_batch_record, \
    insert_order_line_record, insert_allocation_records

"""
TODO: add fixture with inner method to cleanup test data objects
      These tests don't cleanup test data yet
      REVIEW tests 
"""


def test_product_repo_saves_product_batches_to_db(session):
    test_sku = get_random_sku(name='chair')
    batches = [Batch(reference=get_random_batch_ref("b1"),
                     sku=test_sku, quantity=10, eta=datetime.today()),
               Batch(reference=get_random_batch_ref("b2"),
                     sku=test_sku, quantity=20, eta=datetime.today() + timedelta(days=5))]

    p1 = Product(sku=test_sku, batches=batches)
    product_repo = ProductRepository(session)
    product_repo.add(p1)
    session.commit()

    batch_result = [x[0] for x in list(session.execute(text(f'SELECT reference FROM batches WHERE sku="{test_sku}"')))]

    assert len(batch_result) == len(batches)
    for batch in batches:
        assert batch.reference in batch_result


def test_order_lines_can_be_allocated_to_batches(session):
    test_sku = get_random_sku('car')
    test_batch_ref = get_random_batch_ref('batch-a')
    _ = insert_product_record(session, sku=test_sku)
    batch_id = insert_batch_record(session, test_batch_ref, test_sku, 50)
    order_line_id = insert_order_line_record(session, '423', test_sku, 4)
    insert_allocation_records(session, batch_id, order_line_id)

    product_repo = ProductRepository(session)
    batch_obj = list(filter(lambda batch: batch.reference == test_batch_ref, product_repo.get(test_sku).batches))[0]
    assert batch_obj._allocations == {OrderLine(sku=test_sku, quantity=4, order_id="423")}


def test_order_line_can_be_de_allocated_from_batches(session):
    test_sku = get_random_sku('car')
    test_batch_ref = get_random_batch_ref('batch-a')
    _ = insert_product_record(session, sku=test_sku)
    batch_id = insert_batch_record(session, test_batch_ref, test_sku, 50)
    order_line_id_1 = insert_order_line_record(session, 'deallocated', test_sku, 4)
    order_line_id_2 = insert_order_line_record(session, 'allocated', test_sku, 4)
    insert_allocation_records(session, batch_id, order_line_id_1)
    insert_allocation_records(session, batch_id, order_line_id_2)

    product_repo = ProductRepository(session)
    batch_obj = list(filter(lambda batch: batch.reference == test_batch_ref, product_repo.get(test_sku).batches))[0]

    batch_obj.deallocate(OrderLine(sku=test_sku, quantity=4, order_id="deallocated"))

    session.commit()  # committing the session to see if updating repo object reflects the change in DB or not

    batch_obj = list(filter(lambda batch: batch.reference == test_batch_ref, product_repo.get(test_sku).batches))[0]

    assert (OrderLine(sku=test_sku, quantity=4, order_id="deallocated") not in batch_obj._allocations and
            OrderLine(sku=test_sku, quantity=4, order_id="allocated") in batch_obj._allocations)
