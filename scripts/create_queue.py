#!/usr/bin/env python
import os

import boto3


def main() -> None:
    region = os.environ.get("AWS_REGION", "us-east-1")
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
    queue_name = os.environ.get("SQS_QUEUE_NAME", "jobs-indexer-queue")

    sqs = boto3.client("sqs", region_name=region, endpoint_url=endpoint_url)
    response = sqs.create_queue(
        QueueName=queue_name,
        Attributes={
            "VisibilityTimeout": "30",
        },
    )
    print(f"Queue created: {response['QueueUrl']}")


if __name__ == "__main__":
    main()
