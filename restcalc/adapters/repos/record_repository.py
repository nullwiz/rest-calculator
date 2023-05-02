import abc
from restcalculator.domain import model
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from restcalculator.exceptions.custom_exceptions import RecordNotFoundException, RecordExistsException
from restcalculator.exceptions.custom_exceptions import InvalidRecordUpdateException, ForeignKeyViolationException


class AbstractRecordRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, record: model.Record):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, record_id) -> model.Record:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, record: model.Record) -> model.Record:
        raise NotImplementedError

    @abc.abstractmethod
    def get_filtered_query(self, filters: dict, user_id: Optional[str] = None):
        raise NotImplementedError

    @abc.abstractmethod
    def get_deleted(self, record_id) -> model.Record:
        raise NotImplementedError


class SqlAlchemyRecordRepository(AbstractRecordRepository):
    def __init__(self, session):
        self.session = session

    def add(self, record: model.Record) -> model.Record:
        try:
            self.session.add(record)
            self.session.flush()
        except IntegrityError as e:
            if "foreign key constraint" in str(e):
                raise ForeignKeyViolationException(
                    "Foreign key constraint violation: {}".format(e))
            raise RecordExistsException("Record exists with id {}".format(e))
        return record

    def get(self, record_id: str) -> model.Record:
        try:
            return self.session.query(model.Record).filter(model.Record.deleted_at == None).filter_by(id=record_id).one()
        except NoResultFound:
            raise RecordNotFoundException("Record not found")

    def get_deleted(self, record_id: str) -> model.Record:
        try:
            return self.session.query(model.Record).filter(model.Record.deleted_at != None).filter_by(id=record_id).one()
        except NoResultFound:
            raise RecordNotFoundException("Record not found")

    def update(self, record: model.Record) -> model.Record:
        try:
            self.add(record)
        except Exception as e:
            raise InvalidRecordUpdateException(
                "Invalid record update {}".format(e))

    # Used for the utility class for querying, returns query object

    def get_filtered_query(self, filters: dict, user_id: Optional[str] = None):
        query = self.session.query(model.Record)
        # By default, deleted records are not returned by a filter query.
        query = query.filter(model.Record.deleted_at == None)
        if user_id:
            query = query.filter(model.Record.user_id == user_id)
        if filters:
            for key, value in filters.items():
                if hasattr(model.Record, key):
                    query = query.filter(getattr(model.Record, key) == value)
        return query
