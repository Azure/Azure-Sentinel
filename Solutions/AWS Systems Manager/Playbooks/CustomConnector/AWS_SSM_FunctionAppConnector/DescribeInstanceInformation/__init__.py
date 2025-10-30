import logging
import boto3
import json
import azure.functions as func
from os import environ
from botocore.exceptions import ClientError


def main(req: func.HttpRequest) -> func.HttpResponse:
    '''
    Returns the result of AWS API call.

        Parameters:
            req (HttpRequest): Request Parameters
        Returns:
            func.HttpResponse
    '''
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

    # Get Filters, InstanceInformationFilterList, MaxResults and NextToken from the request parameters
    filters = req.params.get('Filters')
    instance_information_filter_list = req.params.get('InstanceInformationFilterList')
    max_results = req.params.get('MaxResults')
    next_token = req.params.get('NextToken')

    if not (filters or instance_information_filter_list or max_results or next_token):
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            filters = req_body.get('Filters')
            instance_information_filter_list = req_body.get('InstanceInformationFilterList')
            max_results = req_body.get('MaxResults')
            next_token = req_body.get('NextToken')
    
    # Set parameter dictionary based on the request parameters
    kwargs = {}
    if filters:
        kwargs['Filters'] = filters
    if instance_information_filter_list:
        kwargs['InstanceInformationFilterList'] = instance_information_filter_list
    if max_results:
        kwargs['MaxResults'] = max_results
    if next_token:
        kwargs['NextToken'] = next_token

    try:
        logging.info('Creating Boto3 SSM Client.')
        ssm_client = boto3.client(
            "ssm",
            region_name=aws_region_name,
            aws_access_key_id=aws_access_key_id, 
            aws_secret_access_key=aws_secret_access_key
        )

        try:
            logging.info('Calling function to describe instance information.')

            results = ssm_client.describe_instance_information(**kwargs)

            logging.info('Call to function describe instance information successful.')

            # Result returns LastPingDateTime, RegistrationDate, LastAssociationExecutionDate and LastSuccessfulAssociationExecutionDate as datetime object which is not JSON serializable
            # Convert datetime object to string
            if results and 'InstanceInformationList' in results:
                for instance in results['InstanceInformationList']:
                    if 'LastPingDateTime' in instance:
                        instance['LastPingDateTime'] = instance['LastPingDateTime'].strftime("%Y-%m-%d %H:%M:%S")
                    if 'RegistrationDate' in instance:
                        instance['RegistrationDate'] = instance['RegistrationDate'].strftime("%Y-%m-%d %H:%M:%S")
                    if 'LastAssociationExecutionDate' in instance:
                        instance['LastAssociationExecutionDate'] = instance['LastAssociationExecutionDate'].strftime("%Y-%m-%d %H:%M:%S")
                    if 'LastSuccessfulAssociationExecutionDate' in instance:
                        instance['LastSuccessfulAssociationExecutionDate'] = instance['LastSuccessfulAssociationExecutionDate'].strftime("%Y-%m-%d %H:%M:%S")

            logging.info('Converting datetime object to string successful.')

            # Return the results
            return func.HttpResponse(
                json.dumps(results),
                headers = {"Content-Type": "application/json"},
                status_code = 200
            )
            
        except ssm_client.exceptions.InternalServerError as ex:
            logging.error(f"Internal Server Exception: {str(ex)}")
            return func.HttpResponse("Internal Server Exception", status_code=500)

        except ssm_client.exceptions.InvalidInstanceId as ex:
            logging.error(f"Invalid InstanceId Exception: {str(ex)}")
            return func.HttpResponse("Invalid InstanceId Exception", status_code=400)

        except ssm_client.exceptions.InvalidNextToken as ex:
            logging.error(f"Invalid NextToken Exception: {str(ex)}")
            return func.HttpResponse("Invalid NextToken Exception", status_code=400)
        
        except ssm_client.exceptions.InvalidInstanceInformationFilterValue as ex:
            logging.error(f"Invalid Instance Information Filter Value Exception: {str(ex)}")
            return func.HttpResponse("Invalid Instance Information Filter Value Exception", status_code=400)
        
        except ssm_client.exceptions.InvalidFilterKey as ex:
            logging.error(f"Invalid Invalid FilterKey Exception: {str(ex)}")
            return func.HttpResponse("Invalid Invalid FilterKey Exception", status_code=400)
        
    
    except ClientError as ex:
        logging.error(f"SSM Client Error: {str(ex)}")
        return func.HttpResponse("SSM Client Error", status_code=401)
        
    except Exception as ex:
        logging.error(f"Exception Occured: {str(ex)}")
        return func.HttpResponse("Internal Server Exception", status_code=500)