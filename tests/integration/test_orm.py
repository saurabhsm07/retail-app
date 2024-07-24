import os

import pytest
from sqlalchemy import text
from domain.models.order_line import OrderLine
from domain.models.product import Product
from tests.conftest import get_random_sku

'''
TODO: Unit test are dependent on external components, needs fixing 
'''


@pytest.mark.skipif(os.environ.get('ENV').lower() != 'local',
                    reason='Tests violates foreign key constraint on product table. in Higher environments (Postgres)')
def test_orderline_mapper_can_load_lines(session):  # (1)
    session.query(OrderLine).delete()
    # TODO test
    session.execute(
        text('INSERT INTO order_lines (order_id, sku, quantity) '
             'VALUES '
             '(\'order1\', \'RED-CHAIR\', 12), '
             '(\'order1\', \'RED-TABLE\', 13),'
             '(\'order2\', \'BLUE-LIPSTICK\', 14)')
    )
    expected = [
        OrderLine("order1", "RED-CHAIR", 12),
        OrderLine("order1", "RED-TABLE", 13),
        OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]

    assert len(session.query(OrderLine).all()) >= len(expected)


@pytest.mark.skipif(os.environ.get('ENV').lower() != 'local',
                    reason='Tests violates foreign key constraint on product table. in Higher environments (Postgres)')
def test_orderine_mapper_can_save_lines(session):
    session.query(OrderLine).delete()
    new_line = OrderLine("order1", "DECORATIVE-WIDGET", 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute(
        text(f'SELECT order_id, sku, quantity FROM \'order_lines\' WHERE order_id = \'{new_line.order_id}\'')))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]


@pytest.mark.skipif(os.environ.get('ENV').lower() != 'local',
                    reason='Tests violates foreign key constraint on product table. in Higher environments (Postgres)')
def test_product_mapper_can_save_products(session):
    session.query(Product).delete()
    p1 = Product(sku=get_random_sku('red_tie'), batches=[])
    session.add(p1)
    session.commit()
    rows = list(session.execute((text(f'SELECT id, sku FROM products WHERE sku=\'{p1.sku}\''))))
    assert rows == [(1, p1.sku)]
