"""
Models for each one of the entities described.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import List, Optional, Any
import uuid
from typing import Optional
import uuid
from restcalculator.service_layer.external_services.random_string_service import RandomStringService


class InsufficientBalance(Exception):
    pass


class InvalidOperationType(Exception):
    pass


class DivisionByZero(Exception):
    pass


class OperationType(Enum):
    ADDITION = "addition"
    SUBSTRACTION = "substraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"
    SQUARE_ROOT = "square_root"
    RANDOM_STRING = "random_string"


class UserRoles(Enum):
    ADMIN = "admin"
    CLIENT = "client"


def enum_to_str(enum: Enum) -> str:
    return enum.value


def str_to_enum(enum_type, string_value):
    return enum_type[string_value]


@dataclass(unsafe_hash=True)
class Operation:
    type: OperationType
    cost: float
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())


@dataclass
class User:
    email: str
    password: str
    balance: float = 20.0
    role: str = UserRoles.CLIENT.value
    deleted_at: Optional[datetime] = None
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())

    def add_operation(self, operation: Operation):
        if operation.cost > self.balance:
            raise InsufficientBalance(
                "Insufficient balance to perform the operation")
        self.balance -= operation.cost


@dataclass(unsafe_hash=True)
class Record:
    operation_id: str
    user_id: str
    amount: float
    user_balance: float
    operation_response: Any
    date: Optional[str] = None
    deleted_at: Optional[datetime] = None
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        self.date = datetime.utcnow()

    def delete(self):
        self.deleted_at = datetime.utcnow()

    def is_deleted(self) -> bool:
        return self.deleted_at is not None
