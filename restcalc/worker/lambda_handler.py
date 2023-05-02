from worker import lambda_worker as worker


def lambda_handler(event, context):
    worker.lambda_handler(event,context)


if __name__ == "__main__":
    lambda_handler()
