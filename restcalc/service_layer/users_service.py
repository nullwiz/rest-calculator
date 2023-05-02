from typing import Optional
from typing import List
from restcalculator.domain import model
from restcalculator.domain.model import UserRoles
from restcalculator.service_layer import unit_of_work
from restcalculator.utils.filter_utility import FilterUtility
from restcalculator.exceptions.custom_exceptions import InvalidUserUpdateException, UserNotFoundException
from restcalculator.utils.hashoor import hash_password
from datetime import datetime


def add_user(user: model.User, uow: unit_of_work.AbstractUnitOfWork):
    # Users are initialized with a balance of 20
    user = uow.users.add(user)
    user_id = user.id
    return user_id


def add_admin(email: str, password: str, uow: unit_of_work.AbstractUnitOfWork):
    # Users are initialized with a balance of 20
    user = model.User(email=email, password=password,
                      role=model.UserRoles.ADMIN.value, balance=100)
    uow.users.add(user)
    return user


def get_user(user_id: str, uow: unit_of_work.AbstractUnitOfWork) -> Optional[model.User]:
    user = uow.users.get(user_id)
    return user


def get_user_by_email(email: str, uow: unit_of_work.AbstractUnitOfWork) -> Optional[model.User]:
    users, _ = FilterUtility.get_filtered_entities(
        uow.users, model.User, {'email': email})
    if len(users) == 0:
        return None
    return users[0]


def list_users(uow: unit_of_work.AbstractUnitOfWork, request_args: dict = None) -> List[model.Record]:
    users, total_pages = FilterUtility.get_filtered_entities(
        uow.users, model.User, request_args)

    return users, total_pages


def update_user(user_id: str, uow: unit_of_work.AbstractUnitOfWork, email: Optional[str] = None, password: Optional[str] = None, balance: Optional[float] = None, role: Optional[UserRoles] = None):
    user = uow.users.get(user_id)
    password = hash_password(password) if password else None
    update_params = {
        'email': email,
        'password': password,
        'role': role,
        'balance': balance,
    }

    for attr, value in update_params.items():
        if value is not None:
            setattr(user, attr, value)

    uow.users.update(user)


def delete_user(email: str, uow: unit_of_work.AbstractUnitOfWork):
    user = uow.users.get(email)
    user.deleted_at = datetime.utcnow()
    # update to graveryard email
    user.email = f"{user.email}-DELETED-{user.deleted_at}"
    uow.users.update(user)
