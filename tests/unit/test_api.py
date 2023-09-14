import pytest
import requests
import uuid

from config import get_api_url
from models import Batch


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batch_ref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_order_id(name=""):
    return f"order-{name}-{random_suffix()}"


def test_valid_request_returns_201_and_allocated_batch_reference(add_stock):
    sku_1 = random_sku('1')
    sku_2 = random_sku('2')
    early_batch = random_batch_ref('early')
    batches = [
        Batch(reference=early_batch, sku=sku_1, quantity=54, eta='2023-01-06'),
        Batch(reference=random_batch_ref('later'), sku=sku_1, quantity=5, eta='2023-01-12'),
        Batch(reference=random_batch_ref('b3'), sku=sku_2, quantity=15, eta=None),
        Batch(reference=random_batch_ref('b4'), sku=sku_2, quantity=15, eta='2023-01-03')
    ]

    add_stock(batches)

    req = {'order_id': random_order_id(), 'sku': sku_1, 'qty': 4}

    res = requests.post(f'{get_api_url()}/allocate', json=req)

    assert res.status_code == 201
    assert res.json()['batch_ref'] == early_batch


def test_invalid_request_returns_400_and_error_message():
    sku_1 = random_sku('1')
    sku_2 = random_sku('2')
    invalid_sku = random_sku('INVALID')

    early_batch = random_batch_ref('early')

    batches = [
        Batch(reference=early_batch, sku=sku_1, quantity=54, eta='2023-01-06'),
        Batch(reference=random_batch_ref('later'), sku=sku_1, quantity=5, eta='2023-01-12'),
        Batch(reference=random_batch_ref('b3'), sku=sku_2, quantity=15, eta=None),
        Batch(reference=random_batch_ref('b4'), sku=sku_2, quantity=15, eta='2023-01-03')
    ]

    req = {'order_id': random_order_id(), 'sku': invalid_sku, 'qty': 4}

    res = requests.post(f'{get_api_url()}/allocate', json=req)

    assert res.status_code == 400
    # assert res.json()['batch_ref'] == early_batch
