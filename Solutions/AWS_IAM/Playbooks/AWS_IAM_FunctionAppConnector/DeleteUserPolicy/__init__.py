import os
import azure.functions as func
import boto3
from botocore.exceptions import ClientError


def main(req: func.HttpRequest) -> func.HttpResponse:
    username = req.params.get('username')
    policyname = req.params.get('policyname')
    if username and policyname:
        try:
            iam = boto3.client('iam',
                               aws_access_key_id=os.environ["AWS_AccessKeyId"],
                               aws_secret_access_key=os.environ["AWS_SecretAccessKey"])
            try:
                iam.delete_user_policy(UserName=username, PolicyName=policyname)
            except iam.exceptions.LimitExceededException or iam.exceptions.NoSuchEntityException as err:
                return func.HttpResponse(str(err), status_code=404)
            return func.HttpResponse("Successfully deleted.", status_code=200)
        except ClientError as err:
            return func.HttpResponse(str(err), status_code=401)
    else:
        return func.HttpResponse("Please pass a username and a policyname on the query string", status_code=400)