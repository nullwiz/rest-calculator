import abc
from restcalculator.domain import model
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict
from restcalculator.exceptions.custom_exceptions import UserExistsException, UserNotFoundException, InvalidUserUpdateException


class AbstractUserRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, user: model.User) -> model.User:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, user_id) -> model.User:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, user: model.User) -> model.User:
        raise NotImplementedError

    @abc.abstractmethod
    def get_filtered_query(self, filters: dict, user_id: Optional[str] = None):
        raise NotImplementedError

    @abc.abstractmethod
    def get_deleted(self, user_id) -> model.User:
        raise NotImplementedError


class SqlAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session):
        self.session = session

    def add(self, user) -> model.User:
        try:
            self.session.add(user)
            # Check for errors preventing commit
            self.session.flush()
        except IntegrityError:
            raise UserExistsException("User already exists")
        return user

    def get(self, user_id):
        try:
            return self.session.query(model.User).filter(model.User.deleted_at == None).filter_by(id=user_id).one()
        except NoResultFound:
            raise UserNotFoundException("User not found")

    def get_deleted(self, user_id):
        try:
            return self.session.query(model.User).filter(model.User.deleted_at != None).filter_by(id=user_id).one()
        except UserNotFoundException:
            raise UserNotFoundException("User not found")

    def update(self, user: model.User):
        # We just add the user here and dont do .merge() cause
        # I already did the logic at the service level.
        try:
            self.session.add(user)
            self.session.flush()
        except Exception as e:
            raise InvalidUserUpdateException(
                "Exception updating user: {}".format(e))

    # Used for the utility class for querying
    def get_filtered_query(self, filters: dict):
        query = self.session.query(model.User)
        # By default, deleted records are not returned.
        query = query.filter(model.User.deleted_at == None)
        if filters:
            for key, value in filters.items():
                if hasattr(model.User, key):
                    query = query.filter(getattr(model.User, key) == value)
        return query
