import pytest

from domain.models.batch import Batch
from domain.models.order_line import OrderLine
from adapters.repository import AbstractRepository
from domain.models.product import Product
from service_layer.services import allocate, InvalidSkuException, deallocate, insert_batch
from service_layer.unit_of_work import AbstractUnitOfWork
from tests.conftest import get_random_sku, get_random_batch_ref


class FakeProductRepository(AbstractRepository):

    def __init__(self, products):
        self._products = set(products)

    def add(self, product):
        self._products.add(product)

    def get(self, sku):
        try:
            return next(product for product in self._products if product.sku == sku)
        except StopIteration:
            return None

    def list(self):
        return self._products


class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


class FakeProductUnitOfWork(AbstractUnitOfWork):

    def __init__(self):
        self.products = FakeProductRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_service_returns_allocated_batch_reference_on_successful_allocation():
    test_sku = get_random_sku('lamp')
    test_batch_ref = get_random_batch_ref("batch")
    order_line = OrderLine("o1", test_sku, 10)
    product = Product(sku=test_sku, batches=[Batch(test_batch_ref, test_sku, 10, None),
                                             Batch("b2", test_sku, 5, None)])

    repo = FakeProductRepository([product])

    result = allocate(order_line, repo, FakeSession())
    assert result == test_batch_ref


def test_service_successfully_deallocates_order_line_from_product():
    test_sku = get_random_sku('lamp')
    test_batch_ref = get_random_batch_ref("batch")

    order_line_1 = OrderLine("o1", test_sku, 10)
    order_line_2 = OrderLine("o2", test_sku, 10)
    order_line_3 = OrderLine("deallocate", test_sku, 41)

    product = Product(test_sku, [Batch(test_batch_ref, test_sku, 100, None)])

    _ = (product.allocate(order_line_1),
         product.allocate(order_line_2),
         product.allocate(order_line_3))

    product_repo = FakeProductRepository([product])

    curr_batch = product_repo.get(test_sku).batches[0]

    curr_allocated_qty = curr_batch.allocated_quantity
    status = deallocate(curr_batch.reference, order_line_3, product_repo, FakeSession())

    assert status
    assert curr_allocated_qty == product_repo.get(test_sku).batches[0].allocated_quantity + order_line_3.quantity


def test_service_raises_error_for_invalid_sku():
    valid_sku = get_random_sku('paint')
    order_line = OrderLine("o1", "invalid_sku", 10)
    product = Product(valid_sku, [Batch("b1", valid_sku, 10, None)])

    repo = FakeProductRepository([product])

    with pytest.raises(InvalidSkuException, match='Invalid sku : invalid_sku'):
        allocate(order_line, repo, FakeSession())


def test_service_commits_changes_on_successful_allocation():
    test_sku = get_random_sku('red-lamp')
    order_line = OrderLine("o1", test_sku, 10)
    product = Product(test_sku, [Batch("b1", test_sku, 10, None)])

    repo = FakeProductRepository([product])

    session = FakeSession()
    _ = allocate(order_line, repo, session)
    assert session.committed


def test_service_can_insert_a_batch_on_valid_request():
    batch_attrs = {"reference": "b_a", "sku": "green-lamp", "quantity": 10, "eta": None}

    aow = FakeProductUnitOfWork()
    status = insert_batch(aow, **batch_attrs)

    assert status
    assert aow.products.get(batch_attrs['sku']).batches[0] == Batch(reference=batch_attrs['reference'],
                                                                    sku=batch_attrs['sku'],
                                                                    quantity=batch_attrs['quantity'],
                                                                    eta=batch_attrs['eta'])
    assert aow.committed
