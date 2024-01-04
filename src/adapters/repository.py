import abc

from domain.models.batch import Batch
from domain.models.order_line import OrderLine
from domain.models.product import Product

from sqlalchemy.exc import NoResultFound

'''
UPDATES:
    - Each domain model object has its own repository abstraction
    - Added additional method get_by_order_id_and_sku to get a unique row from Order Line data.
'''


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, obj):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, key):
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


class ProductRepository(AbstractRepository):

    def __init__(self, session):
        self.session = session

    def add(self, product: Product):
        self.session.add(product)

    def get(self, sku) -> Product | None:
        try:
            return self.session.query(Product).filter_by(sku=sku).one()
        except NoResultFound:
            return
        except Exception as e:
            raise e


class OrderLineRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, order_line):
        self.session.add(order_line)

    def get(self, order_id):
        return self.session.query(OrderLine).filter_by(order_id=order_id).all()

    def get_by_order_id_and_sku(self, order_id, sku) -> OrderLine:
        return self.session.query(OrderLine).filter_by(order_id=order_id, sku=sku).one()
