from datetime import timedelta, datetime

import pytest

from domain.models.batch import Batch
from domain.models.order_line import OrderLine
from domain.models.product import allocate, Product, OutOfStockException


def test_prefer_allocation_to_warehouse_over_shipment():
    test_sku = 'chinese tea-pot'
    warehouse_stock = Batch(reference='batch_1_ref', sku=test_sku, quantity=90, eta=None)
    shipment_stock = Batch(reference='batch_2_ref', sku=test_sku, quantity=90,
                           eta=datetime.today() + timedelta(days=10))

    product = Product(sku=test_sku, batches=[shipment_stock, warehouse_stock])

    line = OrderLine(order_id='1', sku='chinese tea-pot', quantity=5)

    result = allocate(line, product)
    assert result == 'batch_1_ref' \
           and warehouse_stock.available_quantity == 85 and warehouse_stock.allocated_quantity == 5 \
           and shipment_stock.available_quantity == 90


def test_allocation_to_batch_with_minimum_eta():
    test_sku = 'chinese tea-pot'
    shipment_earliest_eta = Batch(reference='batch_1_ref', sku=test_sku, quantity=100,
                                  eta=datetime.today() + timedelta(days=10))
    shipment_medium_eta = Batch(reference='batch_2_ref', sku=test_sku, quantity=100,
                                eta=datetime.today() + timedelta(days=20))
    shipment_latest_eta = Batch(reference='batch_3_ref', sku=test_sku, quantity=100,
                                eta=datetime.today() + timedelta(days=30))
    line = OrderLine(order_id='1', sku='chinese tea-pot', quantity=5)

    product = Product(sku=test_sku,
                      batches=[shipment_earliest_eta, shipment_medium_eta, shipment_latest_eta])
    result = allocate(line, product)
    assert result == 'batch_1_ref' \
           and shipment_earliest_eta.available_quantity == 95 and shipment_earliest_eta.allocated_quantity == 5 \
           and shipment_latest_eta.available_quantity == 100 and shipment_medium_eta.available_quantity == 100


def test_allocate_raises_out_of_stock_exception_when_order_line_cannot_be_allocated():
    test_sku = 'chinese tea-pot'
    cannot_allocated_batches = [
        Batch(reference='batch_1_ref', sku=test_sku, quantity=100, eta=datetime.today() + timedelta(days=10)),
        Batch(reference='batch_2_ref', sku=test_sku, quantity=100, eta=datetime.today() + timedelta(days=20))
    ]
    line = OrderLine(order_id='1', sku='chinese tea-pot', quantity=100)

    product = Product(sku=test_sku, batches=cannot_allocated_batches)
    _ = allocate(line, product)  # emptied batch 1
    _ = allocate(line, product)  # emptied batch 2

    with pytest.raises(OutOfStockException):
        _ = allocate(line, product)
