'''
Module MESRequest to authenticate the Connector plug-in and collect threat events
from the Lookout RISK API.
'''
import json
import sys
import logging
import requests
import os
from .azuresecret_handler import AzureSecretHandler

class MESRequest:
    '''
    Class MESRequest to authenticate the plug-in and collect threat events
    from the Lookout RISK API.
    '''
    def __init__(self, api_domain, ent_name, api_key, vault_uri, key_index=0):
        # static fields
        self.api_domain = api_domain
        self.ent_name = ent_name
        self.api_key = api_key
        
        # populate dynamic variables from the Azure Key Vault
        self.az_kv = AzureSecretHandler(vault_uri)
        
        self.access_token = self.az_kv.get_secret("AccessToken")
        self.refresh_token = self.az_kv.get_secret("RefreshToken")
        self.stream_position = self.az_kv.get_secret("StreamPosition")
        self.is_valid = self.az_kv.get_secret("IsValid")
        self.retry_counter = self.az_kv.get_secret("AuthRetryCounter")
        
        if not self.retry_counter:
            self.retry_counter = 0

        if not self.is_valid:
            self.is_valid = "YES"

        #For very first time, vault doesn't have any stream position saved, so start from 0
        if not self.stream_position:
            self.stream_position = 0

        self.stale_token_errors = ["REVOKED_REFRESH_TOKEN", "EXPIRED_TOKEN"]

    def refresh_header(self):
        '''Format request headers'''
        return {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "cache-control": "no-cache"
        }

    def header(self, token):
        '''Format request headers'''
        return {
            "accept": "application/json",
            "authorization": "Bearer {}".format(token),
            "content-type": "application/x-www-form-urlencoded",
            "cache-control": "no-cache"
        }


    def refresh_oauth(self):
        '''
        Refresh access token using the refresh token
        - Stores the new access token in the Azure Vault and in this object
        - If the refresh token has expired, requests a new refresh and access token
          and stores them in the Azure Vault and in this object
        '''
        try:
            response = requests.post(self.api_domain + "/oauth/token",
                                    data="refresh_token={}&grant_type=refresh_token"
                                    .format(self.refresh_token),
                                    headers=self.refresh_header())
            response_content = json.loads(response.text)
            if 'access_token' in response_content:
                self.access_token = response_content['access_token']
                self.az_kv.set_secret("AccessToken", self.access_token)
                self.az_kv.set_secret("IsValid", "YES")
                self.az_kv.set_secret("AuthRetryCounter", 0)
            else:
                # if the refresh failed, request brand new API credentials
                response = requests.post(self.api_domain + "/oauth/token",
                                        data="grant_type=client_credentials",
                                        headers=self.header(self.api_key))
                response_content = json.loads(response.text)
                if 'access_token' in response_content:
                    self.access_token = response_content['access_token']
                    self.refresh_token = response_content['refresh_token']
                    self.az_kv.set_secret("AccessToken", self.access_token) 
                    self.az_kv.set_secret("RefreshToken", self.refresh_token)
                    self.az_kv.set_secret("IsValid", "YES")
                    self.az_kv.set_secret("AuthRetryCounter", 0)
                else:
                    if response_content['error'] and response_content['error'] == 'invalid_client':
                        # Set flag to avoid unwanted retries in case of invalid key/client
                        self.retry_counter = self.retry_counter + 1
                        self.az_kv.set_secret("AuthRetryCounter", self.retry_counter)
                        if self.retry_counter >= 10:
                            self.az_kv.set_secret("IsValid", "NO")

                    logging.error("Your Lookout application key has expired. " +
                                "Please get a new key and set up this connector app again.\n" +
                                "Go to https://mtp.lookout.com and generate a new key by " +
                                "navigating to System => Application Keys.")
                    logging.error("Exiting...")
                    sys.exit(1)
        except requests.exceptions.ProxyError as e:
            logging.error("Cannot connect to proxy. Remote end closed connection without response")            
        except requests.exceptions.RequestException as e:
            logging.error(e)
            

    def get_oauth(self):
        '''
        Retrieve OAuth tokens from Lookout API
        - Returns the access_token and the refresh_token
        - If the access token is already stored, returns the
          variables stored locally
        '''
        token_json = {}
        if self.access_token:
            logging.info("The access token has been found locally")
            return self.access_token, self.refresh_token

        logging.info("Could not find an access token, getting one now")
        
        try:
            response = requests.post(self.api_domain + "/oauth/token",
                                    data="grant_type=client_credentials",
                                    headers=self.header(self.api_key))
            try:
                token_json = json.loads(response.text)                
            except (AttributeError, ValueError) as e:
                logging.info("Exception when requesting new access token: " + str(e))
                logging.info("Refreshing access token...")
                self.refresh_oauth()

            if 'access_token' in token_json and 'error' not in token_json:
                logging.info("Storing creds in Azure Vault")
                self.access_token = token_json['access_token']
                self.refresh_token = token_json['refresh_token']
                self.az_kv.set_secret("AccessToken", self.access_token)
                self.az_kv.set_secret("RefreshToken", self.refresh_token)
                self.az_kv.set_secret("IsValid", "YES")
                self.az_kv.set_secret("AuthRetryCounter", 0)
                logging.info("Got authenticated")
                return self.access_token, self.refresh_token
            else: 
                if token_json['error'] and token_json['error'] == 'invalid_client':
                    # Set flag to avoid unwanted retries in case of invalid key/client
                    self.retry_counter = self.retry_counter + 1
                    self.az_kv.set_secret("AuthRetryCounter", self.retry_counter)
                    if self.retry_counter >= 10:
                        self.az_kv.set_secret("IsValid", "NO")
                logging.info("Auth API retry count :  " + str(self.retry_counter))
                logging.info("Error in oauth")
                logging.info(str(token_json))
                return False
                
        except requests.exceptions.ProxyError as e:
            logging.error("Cannot connect to proxy. Remote end closed connection without response")            
        except requests.exceptions.RequestException as e:
            logging.error(e)
            
    def get_events(self):
        '''
        Method to collect events from Metis API
        - Gets access token and stream position from Azure Vault
        - Requests events (retries if error HTTP code)
        - Collect events lists from Metis API, returns full list of events
        '''
        
        events = []
        retry_count = 0
        more_events = True
        
        if self.is_valid == "NO" or self.retry_counter >= 10:
            logging.info("Please check API key, Auth API responds with Invalid Client error after 10 retries")
            return events

        if not self.access_token:
            self.get_oauth()

        if self.access_token:
            # Added cycle count to avoid long data polling
            cycle_count = 0
            while more_events and retry_count < 10 and cycle_count < 10 :
                logging.info("Fetching Events from Position {}".format(self.stream_position))
                try:
                    response = requests.get(self.api_domain + "/events?eventType=DEVICE,THREAT,AUDIT",
                                            headers=self.header(self.access_token),
                                            params={"streamPosition": self.stream_position})
                    if response.status_code == 400 and response.json()['errorCode'] in self.stale_token_errors:
                        self.refresh_oauth()
                        continue
                    elif response.status_code != requests.codes.ok:
                        logging.info("Received error code {}, trying again to get events".format(response.status_code))
                        retry_count = retry_count + 1
                        continue
                except requests.exceptions.ProxyError as e:
                    logging.error("Cannot connect to proxy. Remote end closed connection without response")                
                except requests.exceptions.RequestException as e:
                    logging.error(e)                
                    
                cycle_count = cycle_count + 1
                events = events + response.json()['events']
                self.stream_position = response.json()['streamPosition']
                
                #update stream position in Azure Vault
                self.az_kv.set_secret("StreamPosition", self.stream_position)

                more_events = response.json()['moreEvents']
                logging.info("Fetched Event Count {}".format(len(events)))
                logging.info("More Events to Fetch : {}".format(more_events))

            if retry_count >= 10:
                logging.error("Too many failed attempts to retrieve events, shutting down.")
                sys.exit(2)


        return events
