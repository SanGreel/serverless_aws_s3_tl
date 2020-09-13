import os
import logging

import pandas as pd
import boto3

USERS_TABLE = os.environ["USERS_TABLE"]

db_client = boto3.client("dynamodb")
s3 = boto3.client("s3")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def insert_user(user):
    logger.info(
        "user_id {},\n first_name {},\n second_name{}".format(
            user["user_id"], user["first_name"], user["second_name"]
        )
    )
    db_client.put_item(
        TableName=USERS_TABLE,
        Item={
            "userId": {"S": user["user_id"]},
            "firstName": {"S": user["first_name"]},
            "secondName": {"S": user["second_name"]},
        },
    )


def load_data(event, context):
    logger.info("event {}".format(event))

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    file_name = event["Records"][0]["s3"]["object"]["key"]

    if file_name.endswith(".csv"):
        logger.info("Read {} from bucket {}".format(file_name, bucket))

        csv = s3.get_object(Bucket=bucket, Key=file_name)

        df = pd.read_csv(csv["Body"])
        df = df.astype(str)

        df.apply(lambda x: insert_user(x), axis=1)

        response = {"statusCode": 200, "body": {"message": "Data loaded successfully"}}
    else:
        response = {"statusCode": 415, "body": {"message": "Unsupported Media Type"}}

    return response
