from flask import Blueprint, request, jsonify
from restcalculator.service_layer import records_service
from flask import current_app as app
from restcalculator.schemas.schemas import RecordSchema
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from restcalculator.utils.auth_decos import role_required
from restcalculator.uow_factory import create_uow

records_blueprint = Blueprint("records", __name__)

record_schema = RecordSchema()
records_schema = RecordSchema(many=True)


@records_blueprint.route("/records", methods=["GET"])
@jwt_required()
def records():
    current_user_role = get_jwt()["role"]
    current_user_id = get_jwt_identity()

    with create_uow() as uow:
        try:
            records, pages = records_service.list_records(
                uow, user_id=current_user_id, request_args=request.args, is_admin=(current_user_role == "admin"))
        except (KeyError, ValueError) as e:
            return jsonify({"message": f'Invalid filtering: {str(e)}'}), 400

        return jsonify({
            "total_pages": pages,
            "records": records_schema.dump(records)
        }), 200


@records_blueprint.route("/records", methods=["POST"])
@jwt_required()
@role_required("admin")
def add_record():
    data = request.get_json()
    errors = record_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    with create_uow() as uow:
        record_obj = record_schema.load(data)
        record_id = records_service.add_record(record_obj, uow)
        uow.commit()

    with create_uow() as uow:
        record = records_service.get_record(record_id, uow)
        return jsonify(record_schema.dump(record)), 201


@records_blueprint.route("/records/<record_id>", methods=["GET"])
@jwt_required()
def get_record(record_id):
    with create_uow() as uow:
        record = records_service.get_record(record_id, uow)
        return jsonify(record_schema.dump(record)), 200


@records_blueprint.route("/records/<record_id>", methods=["PATCH"])
@jwt_required()
@role_required("admin")
def update_record(record_id):
    data = request.get_json()
    errors = record_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    with create_uow() as uow:
        records_service.update_record(uow, record_id=record_id, **data)
        uow.commit()
        return jsonify({"status": "success", "message": "Record updated"}), 204


@records_blueprint.route("/records/<record_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_record(record_id):
    with create_uow() as uow:
        records_service.delete_record(record_id, uow)
        uow.commit()
        return jsonify({"status": "success", "message": "Record deleted"}), 200
