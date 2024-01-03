import abc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from adapters import repository

'''
UPDATES:
    -   The principle is 1 Unit of work should encompass all our repository objects. 
        But if our repository transactions are mostly executed in Silos then we may choose to define multiple UOW class 
        as per our requirements.
        Currently I am following the second approach.
     
'''


# TODO - maybe define a separate Abstract base class which has the general methods
#  and that is inherited by our AOW repo specific classes if I am set on 1 AOW to 1 Repo approach
class AbstractBatchUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    def __enter__(self):
        return self


DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(
    config.get_db_url(),
))


class BatchRepoUnitOfWork(AbstractBatchUnitOfWork):

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self._session_factory = session_factory

    def __enter__(self):
        self.session = self._session_factory()
        self.batches = repository.BatchRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
