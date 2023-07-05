import pytest
from sqlalchemy import text

from repository import BatchRepository
from models import Batch
from datetime import datetime, timedelta


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
    pytest.fail('todo')


def test_order_lines_can_be_allocated_to_batches(session):
    pytest.fail('todo')
