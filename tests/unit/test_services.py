import pytest

from models import Batch, OrderLine
from repository import AbstractRepository


class FakeRepository(AbstractRepository):

    def __int__(self, batches):
        self._batches = set(batches)

    def add(self, batch: Batch):
        self._batches.add(batch)

    def get(self, reference) -> Batch:
        return next(batch for batch in self._batches if batch.reference == reference)

    def list(self):
        return self._batches

class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    order_line = OrderLine("o1", "red-lamp", 10)
    batch = Batch("b1", "red-lamp", 10)

    repo = FakeRepository(batch)

    result = services.allocate(order_line, repo, FakeSession())
    assert result == 'b1'

def test_service_raises_error_for_invalid_sku():
    order_line = OrderLine("o1", "invalid-sku", 10)
    batch = Batch("b1", "red-lamp", 10)

    repo = FakeRepository(batch)

    result = services.allocate(order_line, repo, FakeSession())

    with pytest.raises(services.InvalidSku, match='Invalid sku : invalid-sku'):
        services.allocate(order_line, repo, FakeSession())

