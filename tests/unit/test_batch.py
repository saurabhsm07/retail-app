import pytest
from datetime import datetime, timedelta

from domain.models.batch import Batch
from domain.models.order_line import OrderLine


def test_batch_allocation_reduces_quantity_by_allocated_quantity():
    batch = Batch(reference='batch_1_ref', sku='RED CHAIRS', quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=5)

    batch.allocate(order_line)
    assert batch.available_quantity == 20


def test_cannot_allocate_when_order_quantity_is_higher_than_available():
    batch = Batch(reference='batch_1_ref', sku='RED CHAIRS', quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=50)

    batch.allocate(order_line)
    assert batch.can_allocate(order_line) is False


def test_can_allocate_when_order_quantity_is_less_than_available():
    batch = Batch(reference='batch_1_ref', sku='RED CHAIRS', quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=2)

    assert batch.can_allocate(order_line) is True


def test_can_allocate_when_order_quantity_is_equal_to_quantity():
    batch = Batch(reference='batch_1_ref', sku='RED CHAIRS', quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=25)

    assert batch.can_allocate(order_line) is True


def test_cannot_allocate_when_sku_do_not_match():
    batch = Batch(reference='batch_1_ref', sku='RED CHAIRS', quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='GREEN CHAIRS', quantity=2)

    assert batch.can_allocate(order_line) is False


def test_cannot_allocate_same_order_multiple_times():
    batch = Batch(reference='batch_1_ref', sku='RED CHAIRS', quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=2)
    batch.allocate(order_line)
    assert batch.can_allocate(order_line) is False


def test_cannot_deallocate_unallocated_order_line():
    batch = Batch(reference='batch_1_ref', sku='mrf_tire', quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='mrf_tire', quantity=2)

    assert batch.deallocate(order_line) is False


def test_can_deallocate_allocated_order_line():
    batch = Batch(reference='batch_1_ref', sku='RED CHAIRS', quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=2)
    batch.allocate(order_line)
    assert batch.deallocate(order_line) is True


def test_de_allocation_increments_batch_available_quantity_by_deallocated_quantity():
    batch = Batch(reference='batch_1_ref', sku='RED CHAIRS', quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=2)
    batch.allocate(order_line)
    prev_batch_available_qty = batch.available_quantity
    batch.deallocate(order_line)
    new_batch_available_qty = batch.available_quantity
    assert (prev_batch_available_qty + order_line.quantity) == new_batch_available_qty


def test_de_allocation_decrements_batch_allocated_quantity_by_deallocated_quantity():
    batch = Batch(reference='batch_1_ref', sku='RED CHAIRS', quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='RED CHAIRS', quantity=2)
    batch.allocate(order_line)
    prev_batch_allocated_qty = batch.allocated_quantity
    batch.deallocate(order_line)
    new_batch_allocated_qty = batch.allocated_quantity
    assert (prev_batch_allocated_qty - order_line.quantity) == new_batch_allocated_qty
