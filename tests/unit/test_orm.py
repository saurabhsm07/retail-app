from sqlalchemy import text
from models import OrderLine


def test_orderline_mapper_can_load_lines(session):  # (1)
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


def test_orderline_mapper_can_save_lines(session):
    new_line = OrderLine("order1", "DECORATIVE-WIDGET", 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute(text('SELECT order_id, sku, quantity FROM "order_lines"')))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]
