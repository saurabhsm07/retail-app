from typing import List

from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy.orm import mapper, relationship

from models.batch import Batch
from models.order_line import OrderLine

metadata = MetaData()

order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("order_id", String(255)),
)

batch = Table(
    "batch",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("quantity", Integer, nullable=False),
    Column("eta", String(255)),
    Column("_allocations", List[OrderLine]),
)


def start_mappers():
    order_lines_mapper = mapper(OrderLine, order_lines)
    batch_mapper = mapper(Batch, batch)
