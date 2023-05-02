from flask import Blueprint, request, jsonify
from restcalculator.service_layer import calculator_service
from restcalculator.schemas.schemas import CalculatorSchema
from flask_jwt_extended import jwt_required, get_jwt
from flask import current_app as app
from restcalculator.uow_factory import create_uow
from marshmallow import ValidationError
from restcalculator.utils.leaky_bucket import UserCacheHandler
from restcalculator.utils.aws_clients import create_s3_client, create_sqs_client
import uuid
from boto3.s3.transfer import TransferManager, TransferConfig
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
import json

calculator_blueprint = Blueprint("calculator", __name__)
calculator_schema = CalculatorSchema()


@calculator_blueprint.route("/process_operation", methods=["POST"])
@jwt_required()
def process_operation():
    data = request.get_json()
    try:
        validated_data = calculator_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user_id = get_jwt()["id"]
    operation_type = validated_data["type"]
    operation_arguments = validated_data.get("arguments", [])

    with create_uow() as uow:
        result = calculator_service.process_operation_core(
            user_id, operation_type, operation_arguments, uow)
        return jsonify(result), 200


@calculator_blueprint.route("/process_csv", methods=["POST"])
@jwt_required()
def handle_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    if not calculator_service.allowed_file(file.filename):
        return jsonify({"error": "Allowed file types are csv"}), 400

    # Check cache if user has exceeded the number of requests
    cache = UserCacheHandler(get_jwt()["id"])
    if not cache.block_or_not():
        return jsonify({"error": "You dont have any available tokens"}), 429
    try:
        s3_client = create_s3_client()
        sqs_client = create_sqs_client()

        task_id = str(uuid.uuid4())
        # Count rows
        total_rows = calculator_service.count_rows(file)
        file.seek(0)
        print("rows: " + str(total_rows))
        # Set up the TransferManager
        transfer_config = TransferConfig()
        transfer_manager = TransferManager(s3_client, config=transfer_config)

        # Define a progress callback function
        def progress_callback(bytes_transferred):
            print(f"{bytes_transferred} bytes transferred")

        # Upload the file to S3 with progress tracking
        future = transfer_manager.upload(
            file, app.config["S3_BUCKET"], f"{task_id}",
            subscribers=[progress_callback]
        )
        future.result()

        message_body = {
            "s3_file": file.filename,
            "user_id": get_jwt()["id"],
            "task_id": task_id,
            "total_rows": str(total_rows)
        }
        message_body = json.dumps(message_body)
        sqs_queue_name = app.config["SQS_QUEUE_NAME"]
        sqs_client.send_message(
            QueueUrl=sqs_client.get_queue_url(
                QueueName=sqs_queue_name)['QueueUrl'],
            MessageBody=message_body
        )
    except ClientError as e:
        return jsonify({"error": f"Error uploading file to S3 or sending message to SQS: {str(e)}"}), 500

    return jsonify({"message": f"File uploaded successfully to S3 and sent to SQS. Task id: {task_id}"}), 200
