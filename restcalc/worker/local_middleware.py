import boto3
import subprocess
import time
import json
import os
import tempfile

sqs_client = boto3.client("sqs", endpoint_url="http://localhost:4566")
queue_url = "http://localhost:4566/000000000000/opworker"

def read_message_from_queue():
    messages = sqs_client.receive_message(
        QueueUrl=queue_url, MaxNumberOfMessages=10)
    if "Messages" not in messages:
        return None
    sqs_message = messages["Messages"][0]
    return sqs_message


while True:
    sqs_message = read_message_from_queue()
    if sqs_message is None:
        print("No messages in queue")
        time.sleep(5)
        continue
    message_body = json.loads(sqs_message['Body'])
    print(sqs_message)
    print(message_body)

    # Step 2: Create a dictionary containing the extracted information
    lambda_event = {
        "Records": [
            {
                "messageId": sqs_message['MessageId'],
                "receiptHandle": sqs_message['ReceiptHandle'],
                "body": sqs_message['Body'],
                "attributes": "thisisatest", 
                "messageAttributes": {},
                "md5OfBody": sqs_message['MD5OfBody'],
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-west-2:123456789012:MyQueue",
                "awsRegion": "us-west-2"
            }
        ]
    }
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        json.dump(lambda_event, temp_file)
        temp_file.close()

        # Step 4: Invoke the Lambda function using the `sls invoke local` command
        subprocess.run(['sls', 'invoke', 'local', '-f',
                        'worker', '-p', temp_file.name])

        # Remove the temporary file after invoking the Lambda function
        os.unlink(temp_file.name)

    time.sleep(5)  # Poll the SQS queue every 5 seconds
