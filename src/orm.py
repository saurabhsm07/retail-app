from typing import List

from sqlalchemy import MetaData, Table, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import mapper, relationship

from models import Batch
from models import OrderLine

metadata = MetaData()

order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("order_id", String(255)),
)

batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True)
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("order_line_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def start_mappers():
    order_lines_mapper = mapper(OrderLine, order_lines)
    mapper(
        Batch,
        batches,
        properties={
            "_allocations": relationship(
                order_lines_mapper, secondary=allocations, collection_class=set,
            )
        }
    )
