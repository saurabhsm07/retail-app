import pytest
from sqlalchemy import text

from adapters.repository import BatchRepository, OrderLineRepository
from domain.models.batch import Batch, OrderLine
from domain.models.order_line import OrderLine
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker


def insert_batch_record(session: sessionmaker, batch_ref: str):
    session.execute(text('insert into batches (reference, sku, quantity) values'
                         f'("{batch_ref}","chair-1",50)'))
    session.commit()
    result = list(session.execute(text('select id from batches where reference=:ref'),
                                  dict(ref=batch_ref))
                  )[0][0]
    return result


def insert_order_line_record(session, order_id):
    session.execute(text('insert into order_lines (sku, quantity, order_id) values'
                         f'("chair-1",3,"{order_id}")'
                         ))
    session.commit()
    result = list(session.execute(text('select id from order_lines where order_id=:order_id'),
                                  dict(order_id=order_id)))[0][0]
    return result


def insert_allocation_records(session, batch_id, order_line_id):
    session.execute(text(f'insert into allocations(batch_id, order_line_id) values({batch_id},{order_line_id})'))
    session.commit()


def test_batch_repo_can_add_batch(session):
    batch_obj = Batch(reference='batch1_ref',
                      sku='chinese tea-pot',
                      quantity=100,
                      eta=datetime.today() + timedelta(days=10))

    batch_session = BatchRepository(session=session)
    batch_session.add(batch_obj)
    session.commit()

    result = list(session.execute(text('SELECT reference,sku,quantity,eta FROM batches')))
    session.rollback()
    assert result == [(batch_obj.reference, batch_obj.sku, batch_obj.quantity, batch_obj.eta.__str__())]
    assert len(result) == 1


def test_order_line_repo_can_add_line(session):
    order_line_obj_1 = OrderLine(sku='chair',
                                 quantity=50,
                                 order_id='4233')
    order_line_obj_2 = OrderLine(sku='table',
                                 quantity=5,
                                 order_id='4233')

    order_line_session = OrderLineRepository(session=session)
    order_line_session.add(order_line_obj_1)
    order_line_session.add(order_line_obj_2)
    session.commit()
    result = list(session.execute(text('SELECT sku,quantity,order_id FROM order_lines where order_id =:order_id'),
                                  dict(order_id=order_line_obj_1.order_id)))

    assert result == [(order_line_obj_1.sku,
                       order_line_obj_1.quantity,
                       order_line_obj_1.order_id),
                      (order_line_obj_2.sku,
                       order_line_obj_2.quantity,
                       order_line_obj_2.order_id)]


def test_order_lines_can_be_allocated_to_batches(session):
    batch_id = insert_batch_record(session, 'batch-a')
    order_line_id = insert_order_line_record(session, '423')
    insert_allocation_records(session, batch_id, order_line_id)

    batch_session = BatchRepository(session)
    batch_obj = batch_session.get('batch-a')

    assert batch_obj._allocations == {OrderLine(sku="chair-1", quantity=3, order_id="423")}


def test_order_line_can_be_de_allocated_from_batches(session):
    batch_id = insert_batch_record(session, 'batch-b')
    order_line_id_1 = insert_order_line_record(session, 'deallocated')
    order_line_id_2 = insert_order_line_record(session, 'allocated')

    insert_allocation_records(session, batch_id, order_line_id_1)
    insert_allocation_records(session, batch_id, order_line_id_2)

    batch_session = BatchRepository(session)
    batch_obj = batch_session.get('batch-b')
    batch_obj.deallocate(OrderLine(sku="chair-1", quantity=3, order_id="deallocated"))

    session.commit()    # committing the session to see if updating repo object reflects the change in DB or not

    batch_session = BatchRepository(session)
    batch_obj = batch_session.get('batch-b')

    assert (OrderLine(sku="chair-1", quantity=3, order_id="deallocated") not in batch_obj._allocations and
            OrderLine(sku="chair-1", quantity=3, order_id="allocated") in batch_obj._allocations)
