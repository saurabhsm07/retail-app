import pytest
from sqlalchemy import create_engine
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
