from sqlalchemy import Table, MetaData, Column, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.orm import registry
from restcalculator.domain import model

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", String(255), primary_key=True),
    Column("email", String(255), unique=True),
    Column("password", String(255)),
    Column("role", String(255), nullable=False, default='client'),
    Column("balance", Float, nullable=False, default=20),
    Column("deleted_at", DateTime, nullable=True),
)

operations = Table(
    "operations",
    metadata,
    Column("id", String(255), primary_key=True),
    Column("type", String(255), unique=True, nullable=False),
    Column("cost", Float, nullable=False),
)

records = Table(
    "records",
    metadata,
    Column("id", String(255), primary_key=True),
    Column("operation_id", ForeignKey("operations.id")),
    Column("user_id", ForeignKey("users.id")),
    Column("amount", Float, nullable=False),
    Column("user_balance", Float, nullable=False, default=10),
    Column("operation_response", JSON, nullable=False),
    Column("date", DateTime, nullable=False),
    Column("deleted_at", DateTime, nullable=True),
)


def start_mappers():
    mapper_reg = registry()
    user_mapper = mapper_reg.map_imperatively(model.User, users)
    operation_mapper = mapper_reg.map_imperatively(model.Operation, operations)

    mapper_reg.map_imperatively(
        model.Record,
        records,
        properties={
            "operation": relationship(operation_mapper),
            "user": relationship(user_mapper),
        },
    )


def create_tables(engine):
    metadata.create_all(engine)
