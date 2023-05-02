# pylint: disable = attribute-defined-outside-init
from __future__ import annotations
import abc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from restcalculator.adapters.repos import operation_repository, record_repository, user_repository
import redis


class AbstractUnitOfWork(abc.ABC):
    records: record_repository.AbstractRecordRepository
    operations: operation_repository.AbstractOperationRepository
    users: user_repository.AbstractUserRepository

    def __init__(self, app):
        self.app = app

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    def refresh(self):
        raise NotImplementedError


def create_default_session_factory(app):
    return sessionmaker(bind=create_engine(app.config['SQLALCHEMY_DATABASE_URI']))


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, app, session_factory=None):
        if session_factory is None:
            session_factory = create_default_session_factory(app)
        self.session_factory = session_factory

    def __enter__(self) -> AbstractUnitOfWork:
        self.session = self.session_factory()
        self.records = record_repository.SqlAlchemyRecordRepository(
            self.session)
        self.operations = operation_repository.SqlAlchemyOperationRepository(
            self.session)
        self.users = user_repository.SqlAlchemyUserRepository(self.session)
        return super().__enter__()

    def __exit__(self, exc_val, exec_type, exc_tb):
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def refresh(self):
        self.session.refresh()


class AbstractFastMemoryDatabase(abc.ABC):
    def __init__(self, app):
        self.app = app

    def __enter__(self) -> AbstractFastMemoryDatabase:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    class WatchError(Exception):
        pass

    @abc.abstractmethod
    def set(self, key, value):
        pass

    @abc.abstractmethod
    def get(self, key):
        pass

    @abc.abstractmethod
    def delete(self, key):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def watch(self):
        pass


class RedisFastMemoryDatabase(AbstractFastMemoryDatabase):

    def __init__(self, app):
        redis_url = app.config['REDIS_URL']
        self.client = redis.Redis.from_url(redis_url)

    def __enter__(self) -> RedisFastMemoryDatabase:
        return self

    def set(self, key, value):
        self.client.set(key, value)

    def get(self, key):
        return self.client.get(key)

    def delete(self, key):
        self.client.delete(key)

    def close(self):
        self.client.close()

    def watch(self, key):
        try:
            self.client.watch(key)
        except redis.WatchError:
            raise self.WatchError("Watch error occurred")
