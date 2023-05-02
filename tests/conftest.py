import time
import pytest
import requests
import os
import uuid
import argparse
from sqlalchemy.exc import OperationalError


def random_uuid():
    return str(uuid.uuid4())


@pytest.fixture(scope="module", autouse=True)
def clean_database():
    def clean_db():
        # Wait for postgres to be ready
        time.sleep(2)
        # run setup each time
        import restcalculator.setup_scripts.setup_fixture as setup_db
        # Parse args to args namespace
        args = {
            "database_uri": "postgresql+psycopg2://postgres:password@localhost:5432/postgres", "teardown": True}
        if os.environ.get("IS_DOCKER"):
            args["database_uri"] = args["database_uri"].replace(
                "localhost", "postgres")
        print("args are")
        print(args)
        args = argparse.Namespace(**args)
        setup_db.main(args)
        # Wait.
        time.sleep(2)

    def teardown_db():
        import restcalculator.setup_scripts.setup_fixture as setup_db
        # Parse args to args namespace
        args = {
            "database_uri": "postgresql+psycopg2://postgres:password@localhost:5432/postgres", "teardown": True}
        if os.environ.get("IS_DOCKER"):
            args["database_uri"] = args["database_uri"].replace(
                "localhost", "postgres")
        print(args)
        args = argparse.Namespace(**args)
        setup_db.main(args)
        # Wait.
        time.sleep(2)

        pass
    clean_db()
    yield
    teardown_db()


@pytest.fixture(scope="session")
def admin_testing_credentials():
    return {
        "email": "defaultadmin@admin.as",
        "password": "adminpass"
    }


@pytest.fixture(scope="session")
def client_testing_credentials():
    return {
        "email": "defaultclient@client.as",
        "password": "Test1234!"
    }
