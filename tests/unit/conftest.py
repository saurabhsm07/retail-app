import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, clear_mappers
from orm import start_mappers, mapper_registry


@pytest.fixture(scope="session")
def session():
    engine = create_engine('sqlite:///:memory:')
    mapper_registry.metadata.create_all(engine)
    start_mappers()
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

            batches_added.add([session.execute(text('select id from batches where sku=:sku and reference=:ref'),
                                               dict(sku=sku, ref=ref))[0][0]])
            skus_added.add([sku])

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
            "DELETE FROM order_lines WHERE sku=:sku", dict(sku=sku),
        )

        session.commit()
