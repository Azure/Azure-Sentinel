""" handles all Microsoft Sentinel apis related functions here """
import base64
import datetime
import requests
import hmac
import hashlib
import logging

logger = logging.getLogger("AS_api")

class logs_api:
    """ 
    class for log analytics api 
    """
    
    def __init__(self, id, key):                            
        """ 
            constructor initializing azure creds.
            id is workspace id and key is primary key
        """
        
        self.customer_id = id
        self.shared_key = key

    @staticmethod
    def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
        """ 
            Build the API signature
        """
        
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")  
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
        return authorization
    
    def post_data(self, body, log_type):
        """ 
            Build and send a request to the POST API 
        """
        
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = logs_api.build_signature(self.customer_id, self.shared_key, rfc1123date, content_length, method, content_type, resource)
        uri = 'https://' + self.customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': log_type,
            'x-ms-date': rfc1123date
        }

        response = requests.post(uri, data=body, headers=headers)
        
        response.raise_for_status()
        logger.info('Accepted')


            
class management_api:
    """ class for api modifiying and getting the data in incidents section of Microsoft Sentinel using management api """
    pass