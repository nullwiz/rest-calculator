import pytest
from unittest.mock import Mock, MagicMock
from restcalculator.domain import model
from restcalculator.domain.model import OperationType
from restcalculator.service_layer import unit_of_work
from restcalculator.service_layer import calculator_service
from restcalculator.exceptions.custom_exceptions import InsufficientFundsException


def test_process_addition_operation():
    user = model.User(email='test@example.com',
                      password='test_password', balance=10)

    operation = model.Operation(type=OperationType.ADDITION.value, cost=5)

    uow = MagicMock(spec=unit_of_work.AbstractUnitOfWork)
    uow.users = Mock()
    uow.users.add.return_value = None

    uow.commit.return_value = None

    args = [1, 2]

    result = calculator_service.process_operation(user, operation, uow, args)
    # Assert that the result is correct
    assert result == sum(args)

    # Assert that the user's balance has been called
    expected_updated_user = model.User(
        email=user.email,
        password=user.password,
        role=user.role,
        id=user.id,
        balance=5  # initial balance is 10, operation cost is 5
    )

    uow.users.add.assert_called_with(expected_updated_user)


def test_process_operation_insufficient_funds():
    user = model.User(email='test@example.com',
                      password='test_password', balance=2)

    operation = model.Operation(type=OperationType.ADDITION, cost=5)

    uow = MagicMock(spec=unit_of_work.AbstractUnitOfWork)

    args = [1, 2]

    with pytest.raises(InsufficientFundsException):
        calculator_service.process_operation(user, operation, uow, args)

    uow.commit.assert_not_called()


def test_process_operation_subtraction():
    user = model.User(email='test@example.com',
                      password='test_password', balance=10)

    operation = model.Operation(type=OperationType.SUBTRACTION.value, cost=5)

    uow = MagicMock(spec=unit_of_work.AbstractUnitOfWork)
    uow.users = Mock()
    uow.users.add.return_value = None

    uow.commit.return_value = None

    args = [5, 2]

    result = calculator_service.process_operation(user, operation, uow, args)
    # Assert that the result is correct
    assert result == 3

    # Assert that the user's balance has been called
    expected_updated_user = model.User(
        email=user.email,
        password=user.password,
        role=user.role,
        id=user.id,
        balance=5  # initial balance is 10, operation cost is 5
    )

    uow.users.add.assert_called_with(expected_updated_user)


def test_process_operation_multiplication():
    user = model.User(email='test@example.com',
                      password='test_password', balance=10)

    operation = model.Operation(
        type=OperationType.MULTIPLICATION.value, cost=5)

    uow = MagicMock(spec=unit_of_work.AbstractUnitOfWork)
    uow.users = Mock()
    uow.users.add.return_value = None

    uow.commit.return_value = None

    args = [3, 4]

    result = calculator_service.process_operation(user, operation, uow, args)
    # Assert that the result is correct
    assert result == 12

    # Assert that the user's balance has been called
    expected_updated_user = model.User(
        email=user.email,
        password=user.password,
        role=user.role,
        id=user.id,
        balance=5  # initial balance is 10, operation cost is 5
    )

    uow.users.add.assert_called_with(expected_updated_user)


def test_process_operation_division():
    user = model.User(email='test@example.com',
                      password='test_password', balance=10)

    operation = model.Operation(type=OperationType.DIVISION.value, cost=5)

    uow = MagicMock(spec=unit_of_work.AbstractUnitOfWork)
    uow.users = Mock()
    uow.users.add.return_value = None

    uow.commit.return_value = None

    args = [8, 2]

    result = calculator_service.process_operation(user, operation, uow, args)
    # Assert that the result is correct
    assert result == 4

    # Assert that the user's balance has been called
    expected_updated_user = model.User(
        email=user.email,
        password=user.password,
        role=user.role,
        id=user.id,
        balance=5  # initial balance is 10, operation cost is 5
    )

    uow.users.add.assert_called_with(expected_updated_user)


def test_process_operation_square_root():
    user = model.User(email='test@example.com',
                      password='test_password', balance=10)

    operation = model.Operation(type=OperationType.SQUARE_ROOT.value, cost=5)

    uow = MagicMock(spec=unit_of_work.AbstractUnitOfWork)
    uow.users = Mock()
    uow.users.add.return_value = None

    uow.commit.return_value = None

    args = [9]

    result = calculator_service.process_operation(user, operation, uow, args)
    # Assert that the result is correct
    assert result == 3
    # Assert that the user's balance has been called
    expected_updated_user = model.User(
        email=user.email,
        password=user.password,
        role=user.role,
        id=user.id,
        balance=5  # initial balance is 10, operation cost is 5
    )

    uow.users.add.assert_called_with(expected_updated_user)
