import pytest
from datetime import datetime, timedelta

from models.batch import Batch
from models.order_line import OrderLine


def test_batch_allocation_reduces_quantity_by_allocated_quantity():
    batch = Batch(id=1, sku='RED CHAIRS', available_quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=5)

    batch.allocate(order_line)
    assert batch.available_quantity == 20


def test_cannot_allocate_when_order_quantity_is_higher_than_available():
    batch = Batch(id=1, sku='RED CHAIRS', available_quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=50)

    batch.allocate(order_line)
    assert batch.can_allocate(order_line) is False


def test_can_allocate_when_order_quantity_is_less_than_available():
    batch = Batch(id=1, sku='RED CHAIRS', available_quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=2)

    assert batch.can_allocate(order_line) is True


def test_can_allocate_when_order_quantity_is_equal_to_available_quantity():
    batch = Batch(id=1, sku='RED CHAIRS', available_quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=25)

    assert batch.can_allocate(order_line) is True


def test_cannot_allocate_when_sku_do_not_match():
    batch = Batch(id=1, sku='RED CHAIRS', available_quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='GREEN CHAIRS', quantity=2)

    assert batch.can_allocate(order_line) is False


def test_cannot_allocate_same_order_multiple_times():
    batch = Batch(id=1, sku='RED CHAIRS', available_quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=2)
    batch.allocate(order_line)
    assert batch.can_allocate(order_line) is False


def test_cannot_deallocate_unallocated_order_line():
    batch = Batch(id=1, sku='mrf tire', available_quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='mrf tire', quantity=2)

    assert batch.deallocate(order_line) is False


def test_can_deallocate_allocated_order_line():
    batch = Batch(id=1, sku='RED CHAIRS', available_quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=2)
    batch.allocate(order_line)
    assert batch.deallocate(order_line) is True


def test_de_allocation_increments_quantity_by_deallocated_quantity():
    batch = Batch(id=1, sku='RED CHAIRS', available_quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=2)
    batch.allocate(order_line)
    current_order_quantity = batch.available_quantity
    batch.deallocate(order_line)
    assert (current_order_quantity + order_line.quantity) == batch.available_quantity


def test_prefer_allocation_to_warehouse_over_shipment():
    pytest.fail('todo')


def test_allocation_to_batch_with_minimum_eta():
    pytest.fail('todo')
