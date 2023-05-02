# This script sets up the database with an admin user, aswell as operations in DB.
# Useful for testing and development purposes
import os
from enum import Enum
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ArgumentError
from restcalculator.domain.model import Operation, User
from restcalculator.adapters.orm import start_mappers, create_tables
from restcalculator.utils.hashoor import hash_password


class OperationType(Enum):
    ADDITION = "addition"
    SUBTRACTION = "substraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"
    SQUARE_ROOT = "square_root"
    RANDOM_STRING = "random_string"


def create_operations(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    for operation_type in OperationType:
        try:
            operation = Operation(
                type=operation_type.value,
                cost=5
            )
            session.add(operation)
            session.commit()
        except Exception as e:
            pass
    session.close()


def create_admin_user(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        admin_user = User(
            email="defaultadmin@admin.as",
            password=hash_password(os.environ.get(
                "ADMIN_PASSWORD", "adminpass")),
            balance=1000,
            role="admin"
        )
        session.add(admin_user)
    except Exception as e:
        pass
    session.commit()
    session.close()


def create_client_user(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        client_user = User(
            email="defaultclient@client.as",
            password=hash_password(os.environ.get(
                "CLIENT_PASSWORD", "Test1234!")),
            balance=20,
            role="client"
        )
        session.add(client_user)
    except Exception as e:
        pass
    session.commit()
    session.close()


def teardown_db(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    session.execute(text("DROP TABLE IF EXISTS records CASCADE"))
    session.execute(text("DROP TABLE IF EXISTS operations CASCADE"))

    session.commit()
    session.close()


def main(args):
    engine = create_engine(args.database_uri)
    if args.teardown:
        teardown_db(engine)
    # check if mappers defined
    try:
        start_mappers()
    except ArgumentError:
        pass
    create_tables(engine)
    create_operations(engine)
    create_admin_user(engine)
    create_client_user(engine)
    print("Initial operations and users have been created.")
    # teardown connection
    engine.dispose()
