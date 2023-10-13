import pytest

from domain.models.batch import Batch
from domain.models.order_line import OrderLine
from adapters.repository import AbstractRepository
from service_layer.services import allocate, InvalidSkuException, deallocate, insert_batch
from service_layer.unit_of_work import AbstractBatchUnitOfWork


class FakeBatchRepository(AbstractRepository):

    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch: Batch):
        self._batches.add(batch)

    def get(self, reference) -> Batch:
        return next(batch for batch in self._batches if batch.reference == reference)

    def list(self):
        return self._batches


class FakeOrderLineRepository(AbstractRepository):

    def __init__(self, line):
        self._lines = set(line)

    def add(self, line: OrderLine):
        self._lines.add(line)

    def get(self, order_id) -> OrderLine:
        return next(line for line in self._lines if line.order_id == order_id)

    def get_by_order_id_and_sku(self, order_id, sku):
        return next(line for line in self._lines if line.order_id == order_id and line.sku == sku)

    def list(self):
        return self._lines


class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


class FakeBatchesUnitOfWork(AbstractBatchUnitOfWork):

    def __init__(self):
        self.batches = FakeBatchRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_service_returns_allocated_batch_reference_on_successful_allocation():
    order_line = OrderLine("o1", "red-lamp", 10)
    batch = Batch("b1", "red-lamp", 10, None)

    repo = FakeBatchRepository([batch])

    result = allocate(order_line, repo, FakeSession())
    assert result == 'b1'


def test_service_successfully_deallocates_order_line_from_batch():
    # TODO - we are currently using allocate domain method directly seems to be the right approach.

    order_line_1 = OrderLine("o1", "red-lamp", 10)
    order_line_2 = OrderLine("o2", "red-lamp", 10)
    order_line_3 = OrderLine("deallocate", "red-lamp", 41)
    batch = Batch("b1", "red-lamp", 100, None)

    batch.allocate(order_line_1)
    batch.allocate(order_line_2)
    batch.allocate(order_line_3)

    batch_repo = FakeBatchRepository([batch])
    order_line_repo = FakeOrderLineRepository([order_line_1, order_line_2, order_line_3])

    batch = batch_repo.get("b1")
    curr_allocated_qty = batch.allocated_quantity
    deallocate(order_line_3.order_id, batch.reference, batch_repo, order_line_repo, FakeSession())

    assert curr_allocated_qty == batch_repo.get("b1").allocated_quantity + order_line_3.quantity


def test_service_raises_error_for_invalid_sku():
    order_line = OrderLine("o1", "invalid-sku", 10)
    batch = Batch("b1", "red-lamp", 10, None)

    repo = FakeBatchRepository([batch])

    with pytest.raises(InvalidSkuException, match='Invalid sku : invalid-sku'):
        allocate(order_line, repo, FakeSession())


def test_service_commits_changes_on_successful_allocation():
    order_line = OrderLine("o1", "red-lamp", 10)
    batch = Batch("b1", "red-lamp", 10, None)

    repo = FakeBatchRepository([batch])

    session = FakeSession()
    result = allocate(order_line, repo, session)
    assert session.committed


def test_service_can_insert_a_batch_on_valid_request():
    batch_attrs = {"reference": "b_a", "sku": "green-lamp", "quantity": 10, "eta": None}

    aow = FakeBatchesUnitOfWork()
    status = insert_batch(aow, **batch_attrs)

    assert status
    assert aow.batches.get(batch_attrs['reference']) == Batch(reference=batch_attrs['reference'],
                                                              sku=batch_attrs['sku'],
                                                              quantity=batch_attrs['quantity'],
                                                              eta=batch_attrs['eta'])
    assert aow.committed
