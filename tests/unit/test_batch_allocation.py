import pytest
from datetime import datetime, timedelta

from models.batch import Batch, OutOfStock, allocate
from models.order_line import OrderLine


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
    batch = Batch(reference='batch_1_ref', sku='mrf tire', quantity=25, eta=datetime.today())
    order_line = OrderLine(order_id=1, sku='mrf tire', quantity=2)

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


def test_prefer_allocation_to_warehouse_over_shipment():
    warehouse_stock = Batch(reference='batch_1_ref', sku='chinese tea-pot', quantity=90, eta=None)
    shipment_stock = Batch(reference='batch_2_ref', sku='chinese tea-pot', quantity=90, eta=datetime.today() + timedelta(days=10))
    line = OrderLine(order_id=1, sku='chinese tea-pot', quantity=5)
    result = allocate(line, [shipment_stock, warehouse_stock])
    assert result['batch_ref'] == 'batch_1_ref' \
           and warehouse_stock.available_quantity == 85 and warehouse_stock.allocated_quantity == 5 \
           and shipment_stock.available_quantity == 90


def test_allocation_to_batch_with_minimum_eta():
    shipment_earliest_eta = Batch(reference='batch_1_ref', sku='chinese tea-pot', quantity=100, eta=datetime.today() + timedelta(days=10))
    shipment_medium_eta = Batch(reference='batch_2_ref', sku='chinese tea-pot', quantity=100, eta=datetime.today() + timedelta(days=20))
    shipment_latest_eta = Batch(reference='batch_3_ref', sku='chinese tea-pot', quantity=100, eta=datetime.today() + timedelta(days=30))
    line = OrderLine(order_id=1, sku='chinese tea-pot', quantity=5)
    result = allocate(line, [shipment_earliest_eta, shipment_medium_eta, shipment_latest_eta])
    assert result['batch_ref'] == 'batch_1_ref' \
           and shipment_earliest_eta.available_quantity == 95 and shipment_earliest_eta.allocated_quantity == 5 \
           and shipment_latest_eta.available_quantity == 100 and shipment_medium_eta.available_quantity == 100


def test_allocate_raises_out_of_stock_exception_when_order_line_cannot_be_allocated():
    cannot_allocated_batches = [
        Batch(reference='batch_1_ref', sku='chinese tea-pot', quantity=100, eta=datetime.today() + timedelta(days=10)),
        Batch(reference='batch_2_ref', sku='chinese tea-pot', quantity=100, eta=datetime.today() + timedelta(days=20)),
        Batch(reference='batch_3_ref', sku='Japanese tea-pot', quantity=1000, eta=datetime.today() + timedelta(days=30))]
    line = OrderLine(order_id=1, sku='chinese tea-pot', quantity=100)

    empty_batch_1_allocation = allocate(line, cannot_allocated_batches)

    empty_batch_2_allocation = allocate(line, cannot_allocated_batches)

    with pytest.raises(OutOfStock):
        out_stock_exception_allocation = allocate(line, cannot_allocated_batches)
