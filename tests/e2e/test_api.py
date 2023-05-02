"""
e2e tests that start always with one admin user and one client user. 
"""

import pytest
import os
import requests

from random import randint
from restcalculator.schemas.schemas import UserSchema, OperationSchema, RecordSchema, PostRecordSchema, PostUserSchema

# Replace this with your API base URL

if os.environ.get("IS_DOCKER"):
    API_BASE_URL = "http://app:8080/api/v1"
    API_LOGIN = "http://app:8080/login"
else:
    API_BASE_URL = "http://127.0.0.1:8080/api/v1"
    API_LOGIN = "http://127.0.0.1:8080/login"


def random_str(prefix='random', length=8):
    return f"{prefix}_{''.join([chr(randint(97, 122)) for _ in range(length)])}"


def before_all(context):
    context.base_url = API_BASE_URL
    context.login_url = API_LOGIN
    context.user_schema = UserSchema()
    context.operation_schema = OperationSchema()
    context.record_schema = RecordSchema()
    context.post_record_schema = PostRecordSchema()
    context.post_user_schema = PostUserSchema()


def get_from_cookiejar(session, cookie_name):
    return session.cookies.get(cookie_name)


@pytest.fixture(scope="function")
def admin_session(admin_testing_credentials):
    def login(email, password) -> requests.Session:
        s = requests.Session()
        r = s.post(
            f"{API_LOGIN}", json={"email": email, "password": password}
        )
        if r.status_code != 200:
            raise Exception("Login failed")
        return s

    session = login(**admin_testing_credentials)
    session.headers.update(
        {"X-CSRF-TOKEN": get_from_cookiejar(session, "csrf_access_token")})

    yield session


@pytest.fixture(scope="function")
def client_session(client_testing_credentials):
    def login(email, password) -> requests.Session:
        s = requests.Session()
        r = s.post(
            f"{API_LOGIN}", json={"email": email, "password": password}
        )
        if r.status_code != 200:
            raise Exception("Login failed")
        return s

    session = login(**client_testing_credentials)
    # Set X-CSRF-TOKEN header
    session.headers.update(
        {"X-CSRF-TOKEN": get_from_cookiejar(session, "csrf_access_token")})
    yield session


def test_client_user_login(client_session):
    r = client_session.get(f"{API_BASE_URL}/records")
    assert r.status_code == 200
    assert get_from_cookiejar(
        client_session, "access_token_cookie") is not None
    assert get_from_cookiejar(
        client_session, "refresh_token_cookie") is not None


def test_admin_user_login(admin_session):
    r = admin_session.get(f"{API_BASE_URL}/users")
    assert r.status_code == 200
    assert get_from_cookiejar(admin_session, "access_token_cookie") is not None
    assert get_from_cookiejar(
        admin_session, "refresh_token_cookie") is not None


def test_admin_calculator(admin_session, admin_testing_credentials):
    # Process a new operation as admin
    r = admin_session.post(
        f"{API_BASE_URL}/process_operation",
        json={"type": "addition", "arguments": [1, 2]})
    assert r.status_code == 200
    assert r.json()["result"] == 3.0
    # Get the userid for the admin by email
    r = admin_session.get(
        f"{API_BASE_URL}/users?email=" + admin_testing_credentials["email"])
    assert r.status_code == 200
    user_id = r.json()["users"][0]["id"]
    # Operation should have created a record for the admin user. We filter by the admins user_id
    r = admin_session.get(
        f"{API_BASE_URL}/records?user_id=" + user_id)
    assert r.status_code == 200
    assert len(r.json()["records"]) == 1
    # Operation cost 5 units
    assert r.json()["records"][0]["amount"] == 5
    assert r.json()["records"][0]["user_id"] == user_id


def test_admin_sees_all_users(admin_session, client_testing_credentials):
    # simple, there are two db users and the admin can see them (himeslf and the client)
    response = admin_session.get(
        f"{API_BASE_URL}/users")
    assert response.status_code == 200
    assert len(response.json()["users"]) == 2
    assert response.json()[
        "users"][0]["email"] == client_testing_credentials["email"]


def test_admin_e2e(admin_session, admin_testing_credentials):
    # Tests that the admin can create, read, update and delete a user (while also seeing all users)
    # Tests that the admin can create, read, update records and delete a record (while seeing all records)

    # Post a new user (client by default)
    response = admin_session.post(
        f"{API_BASE_URL}/users",
        json={"password": random_str(), "email": random_str() + "@example.com"})
    assert response.status_code == 201
    assert "balance" in response.json()
    user_id = response.json()["id"]
    # Update the users balance
    response = admin_session.patch(
        f"{API_BASE_URL}/users/" + user_id,
        json={"balance": 1000})
    assert response.status_code == 204

    # Get operation id "addition"
    response = admin_session.get(f"{API_BASE_URL}/operations")
    assert response.status_code == 200
    for operation in response.json()['operations']:
        if operation["type"] == "addition":
            operation_id = operation["id"]

    if not operation_id:
        pytest.fail("Operation addition not found")

    # Create a new record for the user
    record_payload = {"operation_id": operation_id, "user_balance": 10,
                      "user_id": user_id, "amount": 1000, "operation_response": 20.0}
    response = admin_session.post(
        f"{API_BASE_URL}/records",  json=record_payload
    )
    assert response.status_code == 201
    print(response.json())
    record_id = response.json()["id"]
    # Get all records
    response = admin_session.get(
        f"{API_BASE_URL}/records")

    assert response.status_code == 200
    # We should have only two records, the one created just now, and the one created by the calculator
    assert len(response.json()["records"]) == 2
    # Check record matches what we created
    record_found = False
    for response_record in response.json()["records"]:
        if response_record["id"] == record_id:
            assert response_record["user_balance"] == record_payload["user_balance"]
            assert response_record["user_id"] == record_payload["user_id"]
            assert response_record["amount"] == record_payload["amount"]
            assert response_record["operation_response"] == record_payload["operation_response"]
            record_found = True
            break

    if not record_found:
        pytest.fail("Record not found, or record data is incorrect")

    # Update the record created above
    record_payload = {"user_balance": 20}
    response = admin_session.patch(
        f"{API_BASE_URL}/records/" + record_id,
        json=record_payload)

    assert response.status_code == 204
    get_user = admin_session.get(
        f"{API_BASE_URL}/records/" + record_id)
    assert get_user.json()["user_balance"] == record_payload["user_balance"]

    # Delete the user
    user_id = get_user.json()["user_id"]
    response = admin_session.delete(
        f"{API_BASE_URL}/users/" + user_id)
    assert response.status_code == 200

    # Call again, see if user is present
    response = admin_session.get(f"{API_BASE_URL}/users/" +
                                 user_id)
    assert response.status_code == 404

    # Delete the record
    response = admin_session.delete(
        f"{API_BASE_URL}/records/" + record_id)

    assert response.status_code == 200
    # Call again, see if record is present
    response = admin_session.get(f"{API_BASE_URL}/records/" + record_id)
    assert response.status_code == 404
