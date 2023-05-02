import abc
from restcalculator.domain import model
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from restcalculator.exceptions.custom_exceptions import OperationExistsException, OperationNotFoundException, InvalidOperationUpdateException, ForeignKeyViolationException
from typing import List, Optional, Type


class AbstractOperationRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, operation: model.Operation):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, operation_id) -> model.Operation:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, operation: model.Operation):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, operation: model.Operation):
        raise NotImplementedError

    @abc.abstractmethod
    def get_filtered_query(self, filters: dict = None):
        raise NotImplementedError


class SqlAlchemyOperationRepository(AbstractOperationRepository):
    def __init__(self, session):
        self.session = session

    def add(self, operation: str) -> model.Operation:
        try:
            self.session.add(operation)
            self.session.flush()
        except IntegrityError:
            raise OperationExistsException(
                f"Operation already exists with type {operation.type}")

        return operation

    def get(self, operation_id: str) -> model.Operation:
        try:
            return self.session.query(model.Operation).filter_by(id=operation_id).one()
        except NoResultFound:
            raise OperationNotFoundException(
                f"Operation not found with id {operation_id}")

    def update(self, operation: model.Operation) -> model.Operation:
        try:
            self.add(operation)
        except Exception as e:
            raise InvalidOperationUpdateException(
                f"Error updating operation:".format(e))
    # Used for the utility class for querying, returns Query object

    def get_filtered_query(self, filters: dict = None):
        query = self.session.query(model.Operation)
        if filters:
            for key, value in filters.items():
                if hasattr(model.Operation, key):
                    query = query.filter(
                        getattr(model.Operation, key) == value)
        return query

    def delete(self, operation: model.Operation):
        try:
            self.session.delete(operation)
            self.session.flush()
        except IntegrityError as e:
            raise ForeignKeyViolationException(str(e))
