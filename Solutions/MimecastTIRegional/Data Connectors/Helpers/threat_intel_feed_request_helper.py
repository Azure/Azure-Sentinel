import os

from ..Helpers.date_helper import DateHelper
from ..Models.Request.get_threat_intel_feed import GetThreatIntelFeedRequest
from ..Helpers.threat_intel_feed_response_helper import ThreatIntelFeedResponseHelper
from ..Helpers.graph_api_collector import GraphApiCollector
from ..Helpers.property_mapper import PropertyMapper
from ..Models.Enum.mimecast_endpoints import MimecastEndpoints
from ..Models.Enum.mimecast_response_codes import MimecastResponseCodes
from ..Models.Error.errors import MimecastRequestError
import base64
from hashlib import sha1 as EncryptionAlgo
import hmac
import uuid
import datetime
import requests
import logging
import time
import math


class ThreatIntelFeedRequestHelper:
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
        if hasattr(self, "https_ip") and self.https_ip:
            https_proxy = "https://{https_ip}:{https_port}".format(https_ip=self.https_ip, https_port=self.https_port)
            proxies.update({"https": https_proxy})
        if hasattr(self, "proxy_username") and self.proxy_username:
            auth = "https://{proxy_username}:{proxy_password}@{https_ip}:{https_port}/".format(
                proxy_username=self.proxy_username,
                proxy_password=self.proxy_password,
                https_ip=self.https_ip,
                https_port=self.https_port,
            )
            proxies.update({"https": auth})
        try:
            if proxies:
                response = requests.post(
                    url=self.base_url + request_uri, headers=headers, data=str(payload), timeout=120, proxies=proxies
                )
            else:
                response = requests.post(
                    url=self.base_url + request_uri, headers=headers, data=str(payload), timeout=120
                )
        except Exception as exception:
            exception.extra_message = "Call to " + self.base_url + request_uri + " failed."
            raise MimecastRequestError("Request call to Mimecast failed.")
        if response.status_code == MimecastResponseCodes.quota_exceeded:
            sleep_duration = math.ceil(int(response.headers["X-RateLimit-Reset"]) / 1000)
            logging.info("Rate limit hit. Sleeping for {0} seconds.".format(sleep_duration))
            if sleep_duration > 0:
                time.sleep(math.ceil(15))
            logging.info("Trying again...")
            response = self.send_post_request(payload, request_uri)
        elif response.status_code == MimecastResponseCodes.binding_expired:
            logging.info("Access key expired.")
            raise MimecastRequestError("Access key expired.")
        return response

    def generate_proper_headers(self, request_uri):
        headers = self.make_request_headers(request_uri)
        logging.info("URL: {0} Request ID: {1}".format(self.base_url + request_uri, headers["x-mc-req-id"]))
        return headers

    def make_request_headers(self, request_uri):
        """Generating specific headers from Mimecast credentials."""
        self.request_id = str(uuid.uuid4())
        hdr_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S UTC")
        unsigned_auth_header = "{date}:{req_id}:{uri}:{app_key}".format(
            date=hdr_date, req_id=self.request_id, uri=request_uri, app_key=self.app_key
        )
        hmac_sha1 = hmac.new(
            base64.b64decode(self.secret_key), unsigned_auth_header.encode(), digestmod=EncryptionAlgo
        ).digest()
        sig = base64.encodebytes(hmac_sha1).rstrip()
        headers = {
            "Authorization": "MC " + self.access_key + ":" + sig.decode(),
            "x-mc-app-id": self.app_id,
            "x-mc-date": hdr_date,
            "x-mc-req-id": self.request_id,
            "Content-Type": "application/json",
        }
        return headers

    @staticmethod
    def set_initial_values():
        """Generating default values before execution enters the loop."""
        return [], {}, "", True

    def get_threat_intel_feed(self, start_date, end_date, feed_type):

        response_helper = ThreatIntelFeedResponseHelper()

        self.set_request_credentials(
            email=os.environ["mimecast_email"],
            password=os.environ["mimecast_password"],
            app_id=os.environ["mimecast_app_id"],
            app_key=os.environ["mimecast_app_key"],
            access_key=os.environ["mimecast_access_key"],
            secret_key=os.environ["mimecast_secret_key"],
            base_url=os.environ["mimecast_base_url"],
        )

        next_token = None
        has_more_logs = True
        feed = []
        while has_more_logs:
            model = GetThreatIntelFeedRequest(start_date, end_date, feed_type, next_token)
            response = self.send_post_request(model.payload, MimecastEndpoints.get_threat_intel_feed)
            response_helper.check_response_codes(response, MimecastEndpoints.get_threat_intel_feed)
            success_response = response_helper.parser_threat_intel_feed_success_response(
                response, "csv", True, MimecastEndpoints.get_threat_intel_feed
            )
            has_more_logs, next_token = response_helper.get_next_token(response, next_token)
            feed.extend(success_response)

        return feed

    @staticmethod
    def filter_out_duplicates(feeds):
        sha_mapping = {f["SHA256"]: f for f in feeds}
        unique_feeds = [feed for sha, feed in sha_mapping.items()]
        return unique_feeds

    @staticmethod
    def find_latest_feed(feeds):
        latest_feed = sorted(
            feeds,
            key=lambda x: datetime.datetime.strptime(
                DateHelper.convert_from_mimecast_format(x["Timestamp"]), "%Y-%m-%dT%H:%M:%SZ"
            ),
        )[-1]
        latest_feed = DateHelper.convert_from_mimecast_format(latest_feed["Timestamp"])
        return latest_feed

    def send_feeds_to_azure(self, feeds):
        app_id = os.environ["active_directory_app_id"]
        app_secret = os.environ["active_directory_app_secret"]
        tenant_id = os.environ["active_directory_tenant_id"]

        graph_api_collector = GraphApiCollector()
        property_mapper = PropertyMapper()
        latest_feed = self.find_latest_feed(feeds)
        chunks_of_feeds = self.get_chunks(feeds)
        for chunk in chunks_of_feeds:
            mapped_feeds = property_mapper.map_feeds(chunk)
            headers = graph_api_collector.get_token(app_id, app_secret, tenant_id)
            graph_api_collector.create_threat_indicators(headers, mapped_feeds)

        return latest_feed

    @staticmethod
    def get_chunks(lst):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), 100):
            yield lst[i: i + 100]
