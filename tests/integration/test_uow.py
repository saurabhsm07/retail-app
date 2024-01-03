from sqlalchemy import text
from sqlalchemy.orm import Session

from domain.models.order_line import OrderLine
from service_layer.unit_of_work import BatchRepoUnitOfWork


def insert_batch_in_db(session: Session, reference, sku, quantity, eta):
    session.execute(text('INSERT INTO batches (reference, sku, quantity, eta)'
                         ' VALUES (:ref, :sku, :qty, :eta)'), dict(ref=reference, sku=sku, qty=quantity, eta=eta))
    session.commit()


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


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch_in_db(session, 'b1', 'workbench', 100, None)

    with BatchRepoUnitOfWork(session_factory) as uow:
        batch = uow.batches.get('b1')
        batch.allocate(OrderLine(order_id='44', sku='workbench', quantity=5))
        uow.commit()

    batch_ref = get_allocated_batch_ref(session, '44', 'workbench')

    assert batch_ref == 'b1'
