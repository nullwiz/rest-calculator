"""
Dead simple file to decouple the creation of the unit of work from the rest of the application.
If we need to change later, we can simply change here. Also, this could be based of config. 
"""
from restcalculator.service_layer import unit_of_work
from flask import current_app as app


def create_uow():
    if app.config["UOW_DB_TYPE"] == "sqlalchemy":
        return unit_of_work.SqlAlchemyUnitOfWork(app)
    return "UOW_DB_TYPE not implemented, available options: sqlalchemy"


def create_cache_uow():
    if app.config["UOW_CACHE_TYPE"] == "redis":
        return unit_of_work.RedisFastMemoryDatabase(app)
    return "UOW_CACHE_TYPE not implemented, available options: redis"
