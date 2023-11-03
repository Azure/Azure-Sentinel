from Models.Enum.mimecast_endpoints import MimecastEndpoints
from Models.Enum.mimecast_response_codes import MimecastResponseCodes
from Models.Error.errors import MimecastRequestError
from Models.Request.refresh_access_key import RefreshAccessKeyRequest
import base64
from hashlib import sha1 as EncryptionAlgo
import hmac
import uuid
import datetime
import requests
import logging
import time
import math


class RequestHelper:
    """HttpClient responsible for making proper request headers and sending POST requests to APIs."""

    request_id = None
    app_id = None
    app_key = None
    access_key = None
    secret_key = None
    base_url = None
    email = None
    password = None
    https_ip = None
    https_port = None
    proxy_username = None
    proxy_password = None

    def set_request_credentials(self, app_id, app_key, access_key, secret_key, base_url, email, password):
        """Setting object credentials to be used for generating proper request headers."""
        self.app_id = app_id
        self.app_key = app_key
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.email = email
        self.password = password

    def set_proxy_credentials(self, https_ip, https_port, proxy_username, proxy_password):
        """Setting object proxy credentials to be used for generating proper proxy request configuration."""
        self.https_ip = https_ip
        self.https_port = https_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password

    def send_post_request(self, payload, request_uri):
        """Sending POST requests to Mimecast API."""
        headers = self.generate_proper_headers(request_uri)
        proxies = {}
        if hasattr(self, 'https_ip') and self.https_ip:
            https_proxy = 'https://{https_ip}:{https_port}'.format(https_ip=self.https_ip, https_port=self.https_port)
            proxies.update({'https': https_proxy})
        if hasattr(self, 'proxy_username') and self.proxy_username:
            auth = 'https://{proxy_username}:{proxy_password}@{https_ip}:{https_port}/'.format(
                proxy_username=self.proxy_username,
                proxy_password=self.proxy_password,
                https_ip=self.https_ip,
                https_port=self.https_port)
            proxies.update({'https': auth})
        try:
            if proxies:
                response = requests.post(url=self.base_url + request_uri,
                                         headers=headers,
                                         data=str(payload),
                                         timeout=120,
                                         proxies=proxies)
            else:
                response = requests.post(url=self.base_url + request_uri,
                                         headers=headers,
                                         data=str(payload),
                                         timeout=120)
        except Exception:
            raise MimecastRequestError("Call to " + self.base_url + request_uri + " failed.")

        if response.status_code == MimecastResponseCodes.quota_exceeded:
            sleep_duration = math.ceil(int(response.headers['X-RateLimit-Reset']) / 1000)
            logging.info('Rate limit hit. Sleeping for {0} seconds.'.format(sleep_duration))
            if sleep_duration > 0:
                time.sleep(sleep_duration)
            logging.info('Trying again...')
            response = self.send_post_request(payload, request_uri)
        elif response.status_code == MimecastResponseCodes.binding_expired:
            model = RefreshAccessKeyRequest(self.email, self.access_key)
            logging.info('Access key expired. Refreshing access key.')
            self.send_post_request(model.payload, MimecastEndpoints.refresh_access_key)
            logging.info('Access key refreshed.')
            response = self.send_post_request(payload, request_uri)
        return response

    def generate_proper_headers(self, request_uri):
        """Condition for generating headers for refresh access key request or for all other requests."""
        if request_uri == MimecastEndpoints.refresh_access_key:
            headers = self.make_refresh_token_request_headers()
        else:
            headers = self.make_request_headers(request_uri)
            logging.info("URL: {0} Request ID: {1}".format(self.base_url + request_uri, headers['x-mc-req-id']))
        return headers

    def make_request_headers(self, request_uri):
        """Generating specific headers from Mimecast credentials."""
        self.request_id = str(uuid.uuid4())
        hdr_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S UTC")
        unsigned_auth_header = '{date}:{req_id}:{uri}:{app_key}'.format(
            date=hdr_date,
            req_id=self.request_id,
            uri=request_uri,
            app_key=self.app_key
        )
        hmac_sha1 = hmac.new(
            base64.b64decode(self.secret_key),
            unsigned_auth_header.encode(),
            digestmod=EncryptionAlgo).digest()
        sig = base64.encodebytes(hmac_sha1).rstrip()
        headers = {
            'Authorization': 'MC ' + self.access_key + ':' + sig.decode(),
            'x-mc-app-id': self.app_id,
            'x-mc-date': hdr_date,
            'x-mc-req-id': self.request_id,
            'Content-Type': 'application/json'
        }
        return headers

    def make_refresh_token_request_headers(self):
        """Generating specific headers only for refreshing access key API call."""
        authorization_header_value = base64.b64encode('{0}:{1}'.format(self.email, self.password).encode())
        headers = {
            'Authorization': 'Basic-Cloud {encoded_header}'.format(encoded_header=authorization_header_value.decode('ascii')),
            'x-mc-app-id': self.app_id,
            'Content-Type': 'application/json',
            'x-mc-api-version': '2014.6.1'
        }
        return headers

    @staticmethod
    def set_initial_values():
        """Generating default values before execution enters the loop."""
        return [], {}, '', True
