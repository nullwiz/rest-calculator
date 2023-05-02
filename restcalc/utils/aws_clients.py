
import boto3
from flask import current_app as app


def create_s3_client(lambdalocal = False):
    """
    Passed lambdalocal when using middleware for dev
    """
    if lambdalocal: 
        endpoint_url = "http://localhost:4566"
        print(endpoint_url)
    else:
        endpoint_url = app.config["LOCALSTACK_ENDPOINT"]
    s3_client = boto3.client(
        's3',
        aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=app.config["AWS_SECRET_ACCESS_KEY"],
        region_name=app.config["AWS_REGION"],
        endpoint_url= endpoint_url
    )
    return s3_client


def create_sqs_client(lambdalocal = False):
    """
    Passed lambdalocal when using middleware for dev
    """
    if lambdalocal: 
        endpoint_url = "http://localhost:4566"
    else:
        endpoint_url = app.config["LOCALSTACK_ENDPOINT"]
    sqs_client = boto3.client(
        'sqs',
        aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=app.config["AWS_SECRET_ACCESS_KEY"],
        region_name=app.config["AWS_REGION"],
        endpoint_url=endpoint_url

    )
    return sqs_client

