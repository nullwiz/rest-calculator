"""
The factory necessary for creating the flask app instance and initializing the flask resources
"""
from restcalculator.config import get_config
from flask import Flask, jsonify
from sqlalchemy import create_engine
from restcalculator.adapters import orm
from flask_talisman import Talisman
from flask_jwt_extended import JWTManager
from restcalculator.exceptions.custom_exceptions import (
    RecordNotFoundException, RecordExistsException, ForeignKeyViolationException,
    UserNotFoundException, UserExistsException, ExternalServiceException,
    OperationNotFoundException, OperationExistsException, InsufficientFundsException
)
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    configuration = get_config()
    app.config.from_object(configuration)
    orm.start_mappers()
    initialize_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_error_handlers_blueprints(app)
    with app.app_context():
        # Leaving a context manager here in case we need to do additional stuff
        # For now I just create the db tables if they don't exist with the current
        # session factory and engine
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        orm.create_tables(engine)
        return app


def register_blueprints(app):
    from restcalculator.entrypoints.records import records_blueprint
    from restcalculator.entrypoints.users import users_blueprint
    from restcalculator.entrypoints.operations import operations_blueprint
    from restcalculator.entrypoints.auth import auth_blueprint
    from restcalculator.entrypoints.calculator import calculator_blueprint

    app.register_blueprint(records_blueprint, url_prefix='/api/v1')
    app.register_blueprint(users_blueprint, url_prefix='/api/v1')
    app.register_blueprint(operations_blueprint, url_prefix='/api/v1')
    app.register_blueprint(calculator_blueprint, url_prefix='/api/v1')
    app.register_blueprint(auth_blueprint)


def initialize_extensions(app):
    # For forcing HTTPS and prevent MITM attacks if not local
    if app.config['ENV'] != 'development':
        Talisman(app)
    JWTManager(app)
    CORS(app, origins=[app.config['FRONTEND_URL']],
         supports_credentials=True)


def register_error_handlers_blueprints(app):
    @app.errorhandler(RecordNotFoundException)
    def handle_record_not_found(e):
        return jsonify({"status": "error", "message": e.description}), e.code

    @app.errorhandler(RecordExistsException)
    def handle_record_exists(e):
        return jsonify({"status": "error", "message": e.description}), e.code

    @app.errorhandler(UserNotFoundException)
    def handle_user_not_found(e):
        return jsonify({"status": "error", "message": e.description}), e.code

    @app.errorhandler(UserExistsException)
    def handle_user_exists(e):
        return jsonify({"status": "error", "message": e.description}), e.code

    @app.errorhandler(OperationNotFoundException)
    def handle_operation_not_found(e):
        return jsonify({"status": "error", "message": e.description}), e.code

    @app.errorhandler(OperationExistsException)
    def handle_operation_exists(e):
        return jsonify({"status": "error", "message": e.description}), e.code

    @app.errorhandler(InsufficientFundsException)
    def handle_insufficient_funds(e):
        return jsonify({"status": "error", "message": e.description}), e.code


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error=str(e)), 400

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(error=str(e)), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify(error=str(e)), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify(error=str(e)), 405

    @app.errorhandler(ForeignKeyViolationException)
    def handle_foreign_key_violation(e):
        return jsonify({"status": "error", "message": e.description}), e.code

    # I am a teapot :)
    @app.errorhandler(418)
    def teapot(e):
        return jsonify(error=str(e)), 418

    @app.errorhandler(500)
    def server_error(e):
        # Log the exception.
        app.logger.debug('Server Error: %s', (e.original_exception or e))
        return jsonify(error=str(e)), 500
