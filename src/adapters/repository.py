import abc
from domain.models.batch import Batch
from domain.models.order_line import OrderLine

'''
UPDATES:
    - Each domain model object has its own repository abstraction
    - Added additional method get_by_order_id_and_sku to get a unique row from Order Line data.
'''


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> Batch:
        raise NotImplementedError


class BatchRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(Batch).all()


class OrderLineRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, order_line):
        self.session.add(order_line)

    def get(self, order_id):
        return self.session.query(OrderLine).filter_by(order_id=order_id).all()

    def get_by_order_id_and_sku(self, order_id, sku) -> OrderLine:
        return self.session.query(OrderLine).filter_by(order_id=order_id, sku=sku).one()
