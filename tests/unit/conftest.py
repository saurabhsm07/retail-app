import time
from pathlib import Path

import pytest
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, clear_mappers

import config
from flask_app import app
from orm import start_mappers, mapper_registry


@pytest.fixture(scope="session")
def session():
    engine = create_engine(config.get_db_url())
    mapper_registry.metadata.create_all(engine)
    # start_mappers()
    session = sessionmaker(bind=engine)()
    yield session
    clear_mappers()


@pytest.fixture()
def add_stock(session):
    batches_added = set()
    skus_added = set()

    def _add_stock(batches):
        for ref, sku, qty, eta in batches:
            session.execute(text('insert into batches (reference, sku, quantity, eta) values'
                                 f'("{ref}","{sku}",{qty},"{eta}")'))

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
