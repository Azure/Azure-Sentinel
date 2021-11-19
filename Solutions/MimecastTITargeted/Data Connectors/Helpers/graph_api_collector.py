import datetime
import json
from typing import Optional

import requests
import logging
from msal import ConfidentialClientApplication

from ..Models.Error.errors import GraphAPIRequestError
from ..Models.Enum.microsoft_endpoints import MicrosoftEndpoints


class GraphApiCollector:
    ti_limit = 20

    @staticmethod
    def get_token(app_id, app_secret, tenant_id):
        try:
            app = ConfidentialClientApplication(
                app_id,
                authority=MicrosoftEndpoints.login_url + tenant_id,
                client_credential=app_secret
            )
        except ConnectionError:
            logging.error('Failed to establish connection with GS API. Server is probably not available at the moment.')
            raise GraphAPIRequestError(
                'Failed to establish connection with GS API. Server is probably not available at the moment.')

        result = app.acquire_token_silent(["https://graph.microsoft.com/.default"], account=None)
        if not result:
            result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        headers = {
            'Content-type': "application/json",
            'Authorization': "Bearer " + result['access_token']
        }
        return headers

    @staticmethod
    def update_threat_indicators(headers, data):
        """
        Makes a POST request to update TI indicators.
        :param headers: Header of the POST request.
        :param data: Data for the body of the POST request.
        :returns: json response.
        :raises GraphAPIRequestError: raises an exception
        """
        if data is None:
            logging.error('Request body cannot be empty.')
            raise GraphAPIRequestError('Request body cannot be empty.')

        body = {'value': data}

        response = requests.post(url=MicrosoftEndpoints.ti_base_url + "/updateTiIndicators",
                                 data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 headers=headers,
                                 stream=False)
        if 200 <= response.status_code <= 299:
            logging.info(str(len(data)) + " Threat Indicators updated successfully!")
        else:
            logging.error("Graph API Connector error occurred!")
            logging.error(response.content)
            raise GraphAPIRequestError('Error on Graph API while updating old indicators.')

    @staticmethod
    def create_threat_indicators(headers, data):
        """
        Makes a POST request to create a TI indicator.
        :param headers: Header of the POST request.
        :param data: Data for the body of the POST request.
        :returns: json response.
        :raises GraphAPIRequestError: raises an exception
        """
        if data is None:
            logging.error('Request body cannot be empty.')
            raise GraphAPIRequestError('Request body cannot be empty.')

        body = {'value': data}

        try:
            response = requests.post(url=MicrosoftEndpoints.ti_base_url + "/submitTiIndicators",
                                     data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                     headers=headers,
                                     stream=False)
        except ConnectionError:
            raise GraphAPIRequestError('Error on Graph API while creating new indicators.')

        if 200 <= response.status_code <= 299:
            logging.info(str(len(data)) + " Threat Indicators sent successfully!")
        else:
            logging.error("Graph API Connector error occurred!")
            logging.error(response.content)
            raise GraphAPIRequestError('Error on Graph API while creating new indicators.')

    def find_already_submitted(self, headers, feeds, url: Optional = None):
        f"""
        Makes GET requests to GS API to find duplicates and separate feeds for updating and creation.
        If number of feeds is below ti_limit value the function sends a request for each of the feeds. 
        Othervise the function sends a request to obtain a bulk of data(200 feeds at a time) and check for duplicates in the bulk.
        It continues to do so recursively until the number of remaining unique feeds drop down to ti_limit value or no more data is provided from the API.
        :param headers: Header of the POST request.
        :param feeds: TI Targeted Intel feeds to be checked for duplicates.
        :param url: url for next bulk of data from Windows Defender ATP.
        :returns: json response.
        :raises GraphAPIRequestError: raises an exception
        """
        update_feeds = []
        create_feeds = []
        if len(feeds) < self.ti_limit:
            for feed in feeds:
                logging.info(f"{feed}")
                ti_single_filter = f"?$filter=contains(fileHashValue,{feed['fileHashValue']} and contains(description, 'Mimecast Targeted Threat Intel')"
                try:
                    single_response = requests.get(url=MicrosoftEndpoints.ti_base_url + ti_single_filter,
                                                   headers=headers,
                                                   stream=False)
                except ConnectionError:
                    raise GraphAPIRequestError('Error on Graph API while trying to check for duplicates(single).')

                if 200 <= single_response.status_code <= 299:
                    data = single_response.json()['value']
                    expiration_date = datetime.datetime.strptime(data.get('expirationDateTime'), "%Y-%m-%dT%H:%M:%SZ")
                    now = datetime.datetime.utcnow()
                    if data and expiration_date > now:
                        update_feeds.append({'id': data[0]['id'], 'expirationDateTime': feed['expirationDateTime']})
                    else:
                        create_feeds.append(feed)
                else:
                    logging.error("Graph API Connector error occurred!")
                    logging.error(single_response.content)
                    raise GraphAPIRequestError('Error on Graph API while trying to check for duplicates(single).')
        else:
            multiple_filter_url = f"{MicrosoftEndpoints.ti_base_url}?$select=id,fileHashValue,expirationDateTime,description"
            try:
                response = requests.get(url=url if url else multiple_filter_url,
                                        headers=headers,
                                        stream=False)
            except ConnectionError:
                raise GraphAPIRequestError('Error on Graph API while trying to check for duplicates(multiple).')

            if not (200 <= response.status_code <= 299):
                logging.error("Graph API Connector error occurred!")
                logging.error(response.content)
                raise GraphAPIRequestError('Error on Graph API while trying to check for duplicates(multiple).')

            data = response.json()
            sha_mapping = {f['fileHashValue']: f for f in data['value'] if
                           'Mimecast Targeted Threat Intel' in f['description']}

            duplicates = []
            uniques = []
            for feed in feeds:
                expiration_date = datetime.datetime.strptime(feed.get('expirationDateTime'), "%Y-%m-%dT%H:%M:%SZ")
                now = datetime.datetime.utcnow()

                duplicate = sha_mapping.get(feed['fileHashValue'])
                if duplicate and expiration_date > now:
                    duplicates.append({'id': duplicate['id'], 'expirationDateTime': feed['expirationDateTime']})
                else:
                    uniques.append(feed)

            if duplicates:
                update_feeds.extend(duplicates)

            if uniques:
                if data.get('@odata.nextLink'):
                    feeds_to_update, feeds_to_create = self.find_already_submitted(headers, uniques,
                                                                                   data['@odata.nextLink'])
                    update_feeds.extend(feeds_to_update)
                    create_feeds.extend(feeds_to_create)
                else:
                    create_feeds.append(uniques)

        return update_feeds, create_feeds
