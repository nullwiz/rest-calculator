from flask import Blueprint, request, jsonify
from restcalculator.service_layer import operations_service
from restcalculator.schemas.schemas import OperationSchema
from flask import current_app as app
from flask_jwt_extended import jwt_required
from restcalculator.utils.auth_decos import role_required
from restcalculator.uow_factory import create_uow
from restcalculator.exceptions.custom_exceptions import OperationExistsException

operations_blueprint = Blueprint("operations", __name__)
operation_schema = OperationSchema()
operations_schema = OperationSchema(many=True)


@operations_blueprint.route("/operations", methods=["POST"])
@role_required("admin")
def create_operation():
    data = request.get_json()
    errors = operation_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    op_type = data["type"]
    cost = data["cost"]

    with create_uow() as uow:
        try:
            operation = operations_service.add_operation(op_type, cost, uow)
        except OperationExistsException:
            return jsonify({"status": "error", "message": "Operation already exists"}), 400
        uow.commit()
        return jsonify({"status": "success", "message": "Operation created successfully", "operation": operation_schema.dump(operation)}), 201


@operations_blueprint.route("/operations/<operation_id>", methods=["GET"])
@jwt_required()
def get_operation(operation_id):
    with create_uow() as uow:
        operation = operations_service.get_operation(operation_id, uow)
        return operation_schema.dump(operation), 200


@operations_blueprint.route("/operations", methods=["GET"])
@jwt_required()
def list_operations():
    with create_uow() as uow:
        try:
            operations, pages = operations_service.list_operations(
                request_args=request.args, uow=uow)
        except (KeyError, ValueError) as e:
            return jsonify({"message": f'Invalid filtering fields {str(e)}'}), 400
        return jsonify({
            "total_pages": pages,
            "operations":
            operations_schema.dump(operations)}), 200


@operations_blueprint.route("/operations/<operation_id>", methods=["PATCH"])
@role_required("admin")
def update_operation(operation_id):
    data = request.get_json()
    errors = operation_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    operation_type = data.get("operation_type")
    cost = data.get("cost")

    with create_uow() as uow:
        try:
            updated_operation = operations_service.update_operation(
                operation_id, operation_type, cost, uow)
        except uow.operations.OperationNotFoundException:
            return jsonify({"status": "error", "message": "Operation not found"}), 404
        uow.commit()
        return jsonify({"status": "success", "message": "Operation updated", "operation": operation_schema.dump(updated_operation)}), 200


@operations_blueprint.route("/operations/<operation_id>", methods=["DELETE"])
@role_required("admin")
def delete_operation(operation_id):
    with create_uow() as uow:
        operations_service.delete_operation(operation_id, uow)
        return jsonify({"status": "success", "message": "Operation deleted"}), 200
