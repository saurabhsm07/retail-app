import requests
import uuid

from config import get_api_url
from domain.models.order_line import OrderLine


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batch_ref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_order_id(name=""):
    return f"order-{name}-{random_suffix()}"


# @pytest.mark.usefixtures('restart_api')
def test_valid_allocation_request_returns_201_and_allocated_batch_reference(add_stock):
    sku_1 = random_sku('1')
    sku_2 = random_sku('2')
    early_batch = random_batch_ref('early')
    batches = [
        (early_batch, sku_1, 54, '2023-01-06'),
        (random_batch_ref('later'), sku_1, 5, '2023-01-12'),
        (random_batch_ref('b3'), sku_2, 15, '2023-08-02'),
        (random_batch_ref('b4'), sku_2, 15, '2023-01-03')
    ]

    add_stock(batches)

    req = {'order_id': random_order_id(), 'sku': sku_1, 'qty': 4}

    res = requests.post(f'{get_api_url()}/allocate', json=req)

    assert res.status_code == 201
    assert res.json()['batch_ref'] == early_batch


def test_valid_de_allocation_request_returns_204(add_batch_and_allocations):
    sku_1 = random_sku('1')

    batch = {
        'reference': random_batch_ref('b1'),
        'sku': sku_1,
        'quantity': 54,
        'eta': '2023-01-06'
    }
    deallocated_order_line_id = random_order_id('3')
    order_lines = [
        (random_order_id('1'), sku_1, 10),
        (random_order_id('2'), sku_1, 10),
        (deallocated_order_line_id, sku_1, 41),
    ]
    add_batch_and_allocations(batch, order_lines)

    payload = {'batch_id': batch['reference'], 'order_id': deallocated_order_line_id}
    res = requests.get(f'{get_api_url()}/deallocate', payload)
    assert res.status_code == 204


def test_invalid_de_allocation_request_returns_200(add_batch_and_allocations):
    sku_1 = random_sku('1')

    batch = {
        'reference': random_batch_ref('b1'),
        'sku': sku_1,
        'quantity': 54,
        'eta': '2023-01-06'
    }
    unallocated_order_id = random_order_id('3')
    order_lines = [
        (random_order_id('1'), sku_1, 10),
        (random_order_id('2'), sku_1, 10),
        (unallocated_order_id, sku_1, 41),
    ]
    add_batch_and_allocations(batch, order_lines, unallocated_order_id)

    payload = {'batch_id': batch['reference'], 'order_id': unallocated_order_id}
    res = requests.get(f'{get_api_url()}/deallocate', payload)
    assert res.status_code == 200 and res.json()['message'] == 'cannot deallocate unallocated order line'


# @pytest.mark.usefixtures('restart_api')
def test_invalid_request_returns_400_and_error_message(add_stock):
    sku_1 = random_sku('1')
    sku_2 = random_sku('2')
    invalid_sku = random_sku('INVALID')

    early_batch = random_batch_ref('early')

    batches = [
        (early_batch, sku_1, 54, '2023-01-06'),
        (random_batch_ref('later'), sku_1, 5, '2023-01-12'),
        (random_batch_ref('b3'), sku_2, 15, '2023-08-02'),
        (random_batch_ref('b4'), sku_2, 15, '2023-01-03')
    ]

    add_stock(batches)

    req = {'order_id': random_order_id(), 'sku': invalid_sku, 'qty': 4}

    res = requests.post(f'{get_api_url()}/allocate', json=req)

    assert res.status_code == 400
    # assert res.json()['batch_ref'] == early_batch


def test_request_for_quantity_more_than_available_returns_400_and_error_message(add_stock):
    sku_1 = random_sku('1')
    sku_2 = random_sku('2')

    early_batch = random_batch_ref('early')

    batches = [
        (early_batch, sku_1, 54, '2023-01-06'),
        (random_batch_ref('later'), sku_1, 5, '2023-01-12'),
        (random_batch_ref('b3'), sku_2, 15, '2023-08-02'),
        (random_batch_ref('b4'), sku_2, 15, '2023-01-03')
    ]

    add_stock(batches)

    req = {'order_id': random_order_id(), 'sku': sku_2, 'qty': 400}

    res = requests.post(f'{get_api_url()}/allocate', json=req)

    assert res.status_code == 400
    # assert res.json()['batch_ref'] == early_batch
