import requests
import math
import logging

from urllib.parse import urljoin
from enterpriseinspector.eifunctions import exit_error

class EnterpriseInspector:
    """A small class used for communicating with the ESET Enterprise Inspector server"""
    def __init__(self, base_url, username, password, domain=False, verify=True):
        
        self.base_url = base_url
        self.username = username
        self.password = password
        self.domain = domain
        self.verify = verify
        self.page_size = 100
        self.token = None
        
        if not self.verify:
            logging.warning(
                'Verification of SSL certificate has been disabled!'
            )

        self.login()


    def login(self):

        json = {
            'username': self.username,
            'password': self.password,
            'domain' : self.domain
        }

        self.api_call(
            endpoint='authenticate',
            method='PUT',
            json=json
        )

        if not self.token:
            exit_error('Authentication failure')


    def api_call(self, endpoint, method='GET', json={}, headers={}, params={}):

        # Only need 'GET' and 'PUT' for now
        if method.upper() == 'GET':
            req = requests.get
        elif method.upper() == 'PUT':
            req = requests.put
        else:
            req = requests.get
        
        # Add authorization token to request if present
        if self.token:
            headers.update({
                'Authorization': f'Bearer {self.token}'
            })

        # Remove any extra '/' characters that would cause a 400
        url = urljoin(
            self.base_url,
            f'/api/v1/{endpoint}',
        )

        resp = req(
            url=url,
            json=json,
            headers=headers,
            params=params,
            verify=self.verify
        )
        
        if resp.status_code != 200:
            exit_error(
                f'API call failed: [{resp.status_code}] {resp.content}'
            )

        # Token might get updated between requests
        if 'X-Security-Token' in resp.headers:
            self.token = resp.headers['X-Security-Token']

        return resp


    def detections(self, last_id):

        params = {
            '$orderBy': 'id asc',
            '$filter': f'id gt {last_id}',
            '$count': 1,
        }

        # Get the first batch of detections
        logging.info('Getting list of detections..')

        resp = self.api_call('detections', params=params).json()
        count = resp['count']
        detections = resp['value']
        pages = math.ceil(count / self.page_size)

        logging.info(f'Found {count} detection(s).')

        # Check if there are more pages
        if pages > 1:
            logging.info(f'Detections spread over {pages} pages.')

            for skip in range(self.page_size, count, self.page_size):
                current_page = int(skip / self.page_size + 1)
                logging.info(f'Getting page {current_page}.')
                params.update({
                    '$skip': skip,
                    '$count': 0
                })
                resp = self.api_call('detections', params=params).json()
                detections += resp['value']
        
        return detections


    def enrich(self, detection_details):

        # Resolve "moduleSignatureType"
        signature_types = {
            90: 'Trusted',
            80: 'Valid',
            75: 'AdHoc',
            70: 'None',
            60: 'Invalid',
            0: 'Unkown'
        }

        try:
            signature_type = signature_types[detection_details['moduleSignatureType']]
        except KeyError:
            signature_type = signature_types[0]

        # Resolve "type"
        types = {
            0: 'UnknownAlarm',
            1: 'RuleActivated',
            2: 'MalwareFoundOnDisk',
            3: 'MalwareFoundInMemory',
            4: 'ExploitDetected',
            5: 'FirewallDetection',
            7: 'BlockedAddress',
            8: 'CryptoBlockerDetection',
        }

        try:
            detection_type = types[detection_details['type']]
        except KeyError:
            detection_type = types[0]

        # Create deeplink
        deep_link = urljoin(
            self.base_url,
            f"/console/detection/{detection_details['id']}",
        )

        detection_details.update({
            'type': detection_type,
            'moduleSignatureType': signature_type,
            'deepLink': deep_link
        })

        return detection_details


    def detection_details(self, detection):

        # Get detection details
        resp = self.api_call(f"detections/{detection['id']}").json()

        # Enrich detection details
        detection_details = self.enrich(resp['DETECTION'])

        return detection_details
