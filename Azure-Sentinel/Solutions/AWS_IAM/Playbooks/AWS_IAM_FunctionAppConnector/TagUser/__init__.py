import os
import azure.functions as func
import boto3
from botocore.exceptions import ClientError


def main(req: func.HttpRequest) -> func.HttpResponse:
    username = req.params.get("username")
    tag_key = req.params.get("tag_key")
    tag_value = req.params.get("tag_value")
    if username and tag_key and tag_value:
        try:
            iam = boto3.client(
                "iam",
                aws_access_key_id=os.environ["AWS_AccessKeyId"],
                aws_secret_access_key=os.environ["AWS_SecretAccessKey"],
            )
            try:
                iam.tag_user(
                    UserName=username, Tags=[{"Key": tag_key, "Value": tag_value}]
                )
            except iam.exceptions.NoSuchEntityException as err:
                return func.HttpResponse(str(err), status_code=404)
            except iam.exceptions.InvalidInputException as err:
                return func.HttpResponse(str(err), status_code=400)
            return func.HttpResponse("Successfully added tags.", status_code=200)
        except ClientError as err:
            return func.HttpResponse(str(err), status_code=401)
    else:
        return func.HttpResponse(
            "Please pass a username and tag_key and tag_value on the query string",
            status_code=400,
        )
