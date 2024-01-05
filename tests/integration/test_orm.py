import pytest
from sqlalchemy import text
from domain.models.order_line import OrderLine
from domain.models.product import Product


def test_orderline_mapper_can_load_lines(session):  # (1)
    session.query(OrderLine).delete()
    session.execute(
        text('INSERT INTO order_lines (order_id, sku, quantity) '
             'VALUES '
             '("order1", "RED-CHAIR", 12), '
             '("order1", "RED-TABLE", 13),'
             '("order2", "BLUE-LIPSTICK", 14)')
    )
    expected = [
        OrderLine("order1", "RED-CHAIR", 12),
        OrderLine("order1", "RED-TABLE", 13),
        OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]
    assert session.query(OrderLine).all() == expected


def test_orderine_mapper_can_save_lines(session):
    session.query(OrderLine).delete()
    new_line = OrderLine("order1", "DECORATIVE-WIDGET", 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute(text('SELECT order_id, sku, quantity FROM "order_lines"')))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]


def test_product_mapper_can_save_products(session):
    session.query(Product).delete()
    p1 = Product(sku='red_tie', batches=[])
    session.add(p1)
    session.commit()
    rows = list(session.execute((text('SELECT id, sku FROM products'))))
    assert rows == [(1, p1.sku)]
