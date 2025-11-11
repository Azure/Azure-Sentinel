import logging
import requests
import azure.functions as func
from urllib import response
from os import environ
from hashlib import sha256
from time import time

def __validate_url(url: str) -> bool:
    '''
        Check if given url starts with https://

        Args:
            url(str) - url
        Returns:
            True/False(bool) 
    '''
    if url.startswith("https://"):
        return True
    else:
        return False 

def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info(f'Resource Requested: {func.HttpRequest}')

    # Get url, apikey and secret
    try:
        neustar_ip_geopoint_url = environ['NeustarIPGeoPointAPIUrl']
        neustar_ip_geopoint_apikey = environ['NeustarIPGeoPointAPIKey']
        neustar_ip_geopoint_secret = environ['NeustarIPGeoPointSecret']
    except KeyError as ke:
        logging.error(f'Invalid Settings. {ke.args} configuration is missing.')
        return func.HttpResponse(
             'Invalid Settings. NeustarIPGeoPointEndpointUrl configuration is missing.',
             status_code=500
        )
    
    # Check if url starts with https://
    if not __validate_url(neustar_ip_geopoint_url):
        logging.error(f'Invalid Url. Neustar IP GeoPoint API Url should be prefixed with https://')
        return func.HttpResponse(
             'Invalid Url. Neustar IP GeoPoint API Url should be prefixed with https://',
             status_code=500
        )

    # Make sure endpoint url is ending with forward slash '/'
    if not neustar_ip_geopoint_url.endswith('/'):
        neustar_ip_geopoint_url = neustar_ip_geopoint_url + '/'

    # Get IP Address from the request
    ip_address = req.params.get('IPAddress')
    if not ip_address:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            ip_address = req_body.get('IPAddress')
    
    if not ip_address:
        logging.error(f'Invalid Request. No IP Address in request.')
        return func.HttpResponse(
             'Invalid Request. No IP Address in request.',
             status_code=400
        )

    logging.info(f'IP Address: {ip_address}')

    # Generate signature
    utc_epoch = str(int(time()))
    signature = sha256((neustar_ip_geopoint_apikey + neustar_ip_geopoint_secret + utc_epoch).encode('utf-8')).hexdigest()

    # Costruct url
    url =  neustar_ip_geopoint_url + ip_address + '?apikey=' + neustar_ip_geopoint_apikey + '&sig=' + signature + '&format=json'
    
    # Send request
    response = requests.get(url)

    if response.status_code == 200:
        logging.info(f'Successful Request: {response.status_code} \n {response.url}')
        return func.HttpResponse(
            response.content,
            headers= { "Content-Type": "application/json"}
        )
    else:
        logging.error(f'Bad Request: {response.status_code} \n {response.url}')
        return func.HttpResponse(
             response.content,
             headers= { "Content-Type": "application/json"},
             status_code=response.status_code
        )
