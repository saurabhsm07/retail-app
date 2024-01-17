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
