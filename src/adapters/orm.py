from typing import List

from sqlalchemy import Table, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship, registry

from domain.models.batch import Batch
from domain.models.order_line import OrderLine
from domain.models.product import Product

mapper_registry = registry()

order_lines = Table(
    "order_lines",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("quantity", Integer, nullable=False),
    Column("order_id", String(255)),
)

products = Table(
    "products",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255), unique=True, nullable=False),
    Column("version", Integer, nullable=False)
)

batches = Table(
    "batches",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255), ForeignKey(products.columns.sku)),
    Column("quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True)
)

allocations = Table(
    "allocations",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("order_line_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def start_mappers():
    order_lines_mapper = mapper_registry.map_imperatively(OrderLine, order_lines)

    batch_mapper = mapper_registry.map_imperatively(
        Batch, batches,
        properties={
            "_allocations": relationship(
                order_lines_mapper, secondary=allocations, collection_class=set
            )}
    )

    _ = mapper_registry.map_imperatively(
        Product, products,
        properties={
            "batches": relationship(
                batch_mapper,
                primaryjoin="Product.sku==foreign(Batch.sku)",
                collection_class=list
            )
        })
