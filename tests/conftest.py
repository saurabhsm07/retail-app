import time
import uuid
from typing import Dict, List

import pytest
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, clear_mappers

import config
from domain.models.batch import Batch
from domain.models.order_line import OrderLine
from entrypoints.flask_app import app
from adapters.orm import mapper_registry, start_mappers

'''
Updates:
    -   commented out start_mappers() in session method 
        because we our orm and flask app is tightly coupled and we are already starting a mapper in flask_app module.
        calling the method twice throws ArgumentError: already has a primary mapper defined  
'''


@pytest.fixture(scope="session")
def session_factory():
    session = get_session_obj()
    # start_mappers()
    yield session
    clear_mappers()


@pytest.fixture(scope="session")
def session():
    session = get_session_obj()
    # start_mappers()
    yield session()
    clear_mappers()


def get_session_obj():
    engine = create_engine(config.get_db_url())
    mapper_registry.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    return session


def get_random_suffix():
    return uuid.uuid4().hex[:6]


def get_random_sku(name=""):
    return f"sku-{name}-{get_random_suffix()}"


def get_random_batch_ref(name=""):
    return f"batch-{name}-{get_random_suffix()}"


def get_random_order_id(name=""):
    return f"order-{name}-{get_random_suffix()}"


def insert_product_record(session, sku: str):
    session.execute((text('INSERT INTO PRODUCTS (sku, version) values'
                          f'(\'{sku}\',0)')))
    session.commit()
    result = list(session.execute(text('SELECT id FROM products WHERE sku=:sku'),
                                  dict(sku=sku))
                  )[0][0]

    return result


def insert_batch_record(session, batch_ref: str, sku: str, qty):
    session.execute(text('insert into batches (reference, sku, quantity) values'
                         f'(\'{batch_ref}\',\'{sku}\',{qty})'))
    session.commit()
    result = list(session.execute(text('select id from batches where reference=:ref'),
                                  dict(ref=batch_ref))
                  )[0][0]
    return result


def insert_order_line_record(session, order_id, sku, qty):
    session.execute(text('insert into order_lines (sku, quantity, order_id) values'
                         f'(\'{sku}\',{qty},\'{order_id}\')'
                         ))
    session.commit()
    result = list(session.execute(text('select id from order_lines where order_id=:order_id'),
                                  dict(order_id=order_id)))[0][0]
    return result


def insert_allocation_records(session, batch_id, order_line_id):
    session.execute(text(f'insert into allocations(batch_id, order_line_id) values({batch_id},{order_line_id})'))
    session.commit()


@pytest.fixture()
def add_stock(session):
    batches_added = set()
    skus_added = set()

    def _add_stock(batches):
        for ref, sku, qty, eta in batches:
            if sku not in skus_added:
                session.execute(text('INSERT INTO PRODUCTS (sku, version) values'
                                     f'(\'{sku}\',0)'))

            session.execute(text('insert into batches (reference, sku, quantity, eta) values'
                                 f'(\'{ref}\',\'{sku}\',{qty},\'{eta}\')'))

            batches_added.add(list(session.execute(text('select id from batches where sku=:sku and reference=:ref'),
                                                   dict(sku=sku, ref=ref)))[0][0])
            skus_added.add(sku)

        session.commit()

    yield _add_stock

    for batch_id in batches_added:
        session.execute(
            text("DELETE FROM allocations WHERE batch_id=:batch_id"),
            dict(batch_id=batch_id),
        )
        session.execute(
            text("DELETE FROM batches WHERE id=:batch_id"), dict(batch_id=batch_id),
        )

    for sku in skus_added:
        session.execute(
            text("DELETE FROM order_lines WHERE sku=:sku"), dict(sku=sku),
        )
        session.execute(
            text("DELETE FROM products WHERE sku=:sku"), dict(sku=sku),
        )

    session.commit()


@pytest.fixture()
def add_product_stock_and_allocations(session):
    # TODO: make batches a list of dicts rather than a single object
    order_lines_added = set()
    batch_added = set()
    sku_added = set()

    def _add_batch_and_allocate_lines(batch: Dict, lines: List):
        session.execute(text('INSERT INTO PRODUCTS (sku, version) values'
                             f'(\'{batch["sku"]}\',0)'))

        session.execute(text('insert into batches (reference, sku, quantity, eta) values'
                             f'(\'{batch["reference"]}\',\'{batch["sku"]}\',{batch["quantity"]},\'{batch["eta"]}\')'))

        [[batch_id]] = session.execute(text('SELECT id from batches'
                                            f' where reference =:batch_ref'), dict(batch_ref=batch['reference']))
        batch_added.add(batch_id)
        for order_id, sku, qty in lines:
            session.execute(text('insert into order_lines (order_id, sku, quantity) values'
                                 f'(\'{order_id}\',\'{sku}\',{qty})'))
            order_lines_added.add(order_id)

        order_line_ids = []
        for order_id in order_lines_added:
            order_line_ids.append(
                list(session.execute(text('SELECT id FROM order_lines WHERE order_id = :order_id'),
                                     {'order_id': order_id}))[0][0])

        for line_id in order_line_ids:
            session.execute(text('insert into allocations (batch_id, order_line_id) values'
                                 f'({batch_id},{line_id})'))
        session.commit()

    yield _add_batch_and_allocate_lines

    for sku in sku_added:
        session.execute(
            text("DELETE FROM products WHERE sku=:sku"),
            dict(sku=sku),
        )

    for batch_id in batch_added:
        session.execute(
            text("DELETE FROM allocations WHERE batch_id=:batch_id"),
            dict(batch_id=batch_id),
        )
        session.execute(
            text("DELETE FROM batches WHERE id=:batch_id"), dict(batch_id=batch_id),
        )

    for order_id in order_lines_added:
        session.execute(
            text("DELETE FROM order_lines WHERE order_id=:order_id"), dict(order_id=order_id),
        )

    session.commit()


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture()
def restart_api():
    app.run(host='0.0.0.0', port=80, debug=True)
    time.sleep(0.5)
    return
#     # wait_for_webapp_to_come_up()
