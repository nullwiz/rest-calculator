from restcalculator.service_layer.calculator_service import process_operation_core
from restcalculator.utils.aws_clients import create_s3_client, create_sqs_client
from restcalculator.utils.leaky_bucket import UserCacheHandler
from restcalculator.uow_factory import create_uow
from restcalculator.factory import create_app
from datetime import datetime
import csv
from io import StringIO, BytesIO
import json
import ast

app = create_app()

with app.app_context():
    if app.config["ENV"] == "development":
        s3_client = create_s3_client(lambdalocal=True)
        sqs_client = create_sqs_client(lambdalocal=True)
    else:
        s3_client = create_s3_client()
        sqs_client = create_sqs_client()
    queue_url = sqs_client.get_queue_url(
        QueueName=app.config["SQS_QUEUE_NAME"])["QueueUrl"]


def count_rows_in_s3_csv(bucket, key):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    row_count = 0
    # Inefficent in terms of it loads the whole object to memory.
    # Only way there is to coutn all rows. Maybe
    # request the user to pass the total rows
    with BytesIO(response['Body'].read()) as s3_file:
        csv_reader = csv.reader(s3_file.read().decode("utf-8").splitlines())
        row_count = sum(1 for row in csv_reader)
    return row_count


def lambda_handler(event, context):
    with app.app_context():
        try:
            print("Processing message...")
            start_time = datetime.now()

            message = event['Records'][0]
            print(f"Processing message: {message}")
            message_body = json.loads(message['body'])
            s3_file = message_body["s3_file"]
            user_id = message_body["user_id"]
            task_id = message_body["task_id"]
            total_rows = int(message_body["total_rows"])

            # Initialize UserCacheHandler
            cache = UserCacheHandler(user_id)
            if cache.get_task(task_id) is None:
                cache.add_new_task(task_id, total_rows)
            if cache.get_task(task_id)["status"] == "processing":
                # total_rows = count_rows_in_s3_csv("buckeeto", s3_file)
                # Do something when it's still processign?
                pass

            # Get the file object from S3
            s3_response = s3_client.get_object(
                Bucket=app.config["S3_BUCKET"], Key=task_id)
            file_stream = s3_response['Body']
            if file_stream is None:
                cache.update_error(task_id, "File not found in S3", 0)
                raise Exception("File not found in S3")

            chunk_size = 10

            # Read and process the CSV file in chunks
            reader = csv.reader(
                StringIO(file_stream.read().decode('utf-8')), delimiter=',')
            # skip header
            next(reader)
            chunk = []
            lines_processed = cache.get_lines_processed(task_id)
            cache.update_task(task_id, "processing")
            for row_number, row in enumerate(reader):
                if row_number < lines_processed:
                    continue

                chunk.append(row)
                if len(chunk) >= chunk_size:
                    for line in chunk:
                        with create_uow() as uow:
                            print(f'lines {line[0]} , {line[1]}')
                            process_operation_core(
                                user_id, line[0], ast.literal_eval(line[1]), uow)
                        lines_processed += 1

                    chunk = []

                    # Update the cache with the progress
                    percentage = (chunk_size / total_rows) * 100
                    print(f'lines processed: {lines_processed}')
                    cache.update_progress(task_id, percentage, lines_processed)

                    # Check if the Lambda function is about to reach its timeout limit
                    elapsed_time = datetime.now() - start_time
                    elapsed_minutes = elapsed_time.total_seconds() / 60
                    # Lambda timeout is 15m
                    if elapsed_minutes + 5 > 15:
                        print("Exiting due to timeout.")
                        return

            # Process remaining lines in the chunk
            if chunk:
                for line in chunk:
                    with create_uow() as uow:
                        process_operation_core(
                            user_id, line[0], ast.literal_eval(line[1]), uow)

                # Update the cache with the progress
            cache.update_progress(task_id, 100, total_rows)
            cache.update_task(task_id, "completed")
            # At this point, we can delete the message from the queue.
            sqs_client.delete_message(
                QueueUrl=queue_url, ReceiptHandle=message['receiptHandle'])
            print("Message processed successfully")
        except Exception as e:
            print("Some error happened: " + str(e))
            cache.update_error(task_id, str(e), 0)
            sqs_client.delete_message(
                QueueUrl=queue_url, ReceiptHandle=message['receiptHandle'])
