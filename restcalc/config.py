"""
Flask config
"""
from os import environ
from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta


class Config:
    """ Base config """
    JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY')
    ADMIN_PASSWORD = environ.get("ADMIN_PASSWORD")
    JWT_TOKEN_LOCATION = ["cookies"]
    RANDOM_STRING_API_URL = "https://api.random.org/json-rpc/4/invoke"
    RANDOM_STRING_API_KEY = environ.get("RANDOM_STRING_API_KEY")
    UOW_DB_TYPE = "sqlalchemy"
    UOW_CACHE_TYPE = "redis"


class DevelopmentConfig(Config):
    """ Development config """
    ENV = 'development'

    DEBUG = True
    in_docker = environ.get('IN_DOCKER')
    postgres_host = "postgres" if in_docker else "localhost"
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://postgres:password@{postgres_host}:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # For debugging purposes and checking query performance
    SQLALCHEMY_ECHO = True
    JWT_ACCESS_TOKEN_EXPIRES = False
    FRONTEND_URL = "http://localhost:3000"
    S3_BUCKET = 'buckeeto'
    SQS_QUEUE_NAME = 'opworker'
    AWS_ACCESS_KEY_ID = 'test'
    AWS_SECRET_ACCESS_KEY = 'test'
    AWS_REGION = 'us-east-1'
    LOCALSTACK_ENDPOINT = 'http://localstack:4566'
    redis_host = "redis" if in_docker else "localhost"
    REDIS_URL = f'redis://{redis_host}:6379/0'


class ProductionConfig(Config):
    """ Production config """
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = environ.get('AWS_PGSQL_PATH')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_SAMESITE = "None"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_COOKIE_CSRF_PROTECT = True
    FRONTEND_URL = environ.get('FRONTEND_URL')


def get_config():
    CONFIG_TYPE = environ.get(
        'CONFIG_TYPE', default='development')
    return config[CONFIG_TYPE]


config = {
    'development': 'restcalculator.config.DevelopmentConfig',
    'production': 'restcalculator.config.ProductionConfig'
}
