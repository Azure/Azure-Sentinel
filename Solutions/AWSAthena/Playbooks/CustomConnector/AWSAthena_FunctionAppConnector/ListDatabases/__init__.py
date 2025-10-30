import logging
import boto3
import json
import azure.functions as func
from botocore.exceptions import ClientError
from os import environ


def main(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info(f'Resource Requested: {func.HttpRequest}')

    # Get AWS ID and Key
    try:
        aws_access_key_id = environ['AWSAccessKeyID']
        aws_secret_access_key = environ['AWSSecretAccessKey']
        aws_region_name = environ['AWSRegionName']

    except KeyError as ke:
        logging.error(f'Invalid Settings. {ke.args} configuration is missing.')
        return func.HttpResponse(
             'Invalid Settings. AWS Access ID/Key configuration is missing.',
             status_code=500
        )

    # Get Data Catalog Name from the request parameter
    catalog_name = req.params.get('CatalogName')

    if not catalog_name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            catalog_name = req_body.get('CatalogName')

    if catalog_name:
        
        try:
            logging.info(f'Creating Boto3 Athena Client.')
            athena_client = boto3.client(
                "athena",
                region_name=aws_region_name,
                aws_access_key_id=aws_access_key_id, 
                aws_secret_access_key=aws_secret_access_key
            )
            
            try:
                # Get the list of databases for given data catalog
                logging.info(f'Sending Request for data catalog.')
                response = athena_client.list_databases(CatalogName=catalog_name)
                dblist = response['DatabaseList']

                # Parse dblist to get the dbnames and format as json
                dbnames = []
                for db in dblist:
                    dbnames.append(db['Name'])

                results = {"Databases" : dbnames}

                return func.HttpResponse(
                    json.dumps(results),
                    headers = {"Content-Type": "application/json"},
                    status_code = 200
                )
        
            except athena_client.exceptions.InternalServerException as ex:
                logging.error(f"Internal Server Error: {str(ex)}")
                return func.HttpResponse("Internal Server Error", status_code=404)

            except athena_client.exceptions.InvalidRequestException as ex:
                logging.error(f"Invalid Request Exception: {str(ex)}")
                return func.HttpResponse("Invalid Request Exception: Not a valid CatalogName", status_code=400)
            
            except athena_client.exceptions.MetadataException as ex:
                logging.error(f"Metadata Exception: {str(ex)}")
                return func.HttpResponse("Metadata Exception", status_code=400)

        except ClientError as ex:
            logging.error(f"Athena Client Error: {str(ex)}")
            return func.HttpResponse("Athena Client Error", status_code=401)
        
        except Exception as ex:
            logging.error(f"Exception Occured: {str(ex)}")
            return func.HttpResponse("Internal Server Exception", status_code=500)

    else:
        return func.HttpResponse(
             "Please pass CatalogName in the query string.",
             status_code=400
        )
