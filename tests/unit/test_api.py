import pytest
import requests
import uuid

from config import get_api_url


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batch_ref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


def test_valid_request_returns_201_and_allocated_batch_reference():
    requests.post(f'{get_api_url()}/allocate')


def test_invalid_request_returns_400_and_error_message():
    pytest.todo('fail')
