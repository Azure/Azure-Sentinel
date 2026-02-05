"""
Azure Function to fetch Email Threat Detection messages from the Cisco ETD Api and send the mesages to Sentinel to be able to analyze them on Log Analytics.
"""
import logging
import datetime
import json
import requests
import hashlib
import hmac
import base64
import os
from http import HTTPStatus
import azure.functions as func

# Global variables for Connector
APIKEY = os.environ.get("ApiKey","")
CLIENTID = os.environ.get("ClientId","")
CLIENTSECRET = os.environ.get("ClientSecret","")
WORKSPACEID = os.environ.get("WorkspaceID","")
WORKSPACESHAREDKEY= os.environ.get("SharedKey","")
VERDICTS = os.environ.get("Verdicts","malicious").split(",")
REGION = os.environ.get("Region","us")
TABLENAME = "CiscoETD"
CHUNKSIZE = 20
PAGESIZE = 50
APISCHEME = "https://api."
APITOKENENDPOINT = ".etd.cisco.com/v1/oauth/token"
APIMESSAGEENDPOINT = ".etd.cisco.com/v1/messages/search"
LAST = "Last"
NEXT = "Next"
UTCZONE = "Z"

def retryRequest(url, headers, jsonData=None, retryCount=3):
    """
    Function to post messages and retry on failure
    :param url: url to post messages to
    :param headers: headers to add to the post call 
    :param jsonData: payload for the post call
    :param retryCount: number of retries on failure, default value is set to 3
    :return: response if successful, None otherwise
    """
    while retryCount > 0:
        try:
            response = requests.post(url, headers=headers, json=jsonData, timeout=5)
        except Exception as err:
            logging.error(f"Error during the request: {err}")
            retryCount -= 1
        else:
            if response.status_code == HTTPStatus.OK:
                logging.info("Post request successful")
                return response
            elif response.status_code == HTTPStatus.UNAUTHORIZED:
                logging.error("Authorization Error while calling post request")
                return response
            else:
                logging.error(f"Post request failed, retrying... status code: {response.status_code}")
                retryCount -= 1     
    return None

class ETD():
    """
    Class ETD is responsible for fetching the messages from ETD API
    """
    def __init__(self, apiKey, clientId, clientSecret, verdicts, region, lastExecutedTime, currentTime):
        self.apiKey = apiKey
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.messageFilter = [v.strip() for v in verdicts]
        self.secretToken = ""
        self.region = region
        self.lastExecutedTime = lastExecutedTime
        self.currentUtcTime = currentTime
        self.tokenUrl = APISCHEME + self.region + APITOKENENDPOINT
        self.messageUrl = APISCHEME + self.region + APIMESSAGEENDPOINT

    def generateToken(self):
        """
        Function to generate the token for ETD message search api
        :return: True if successful, False otherwise
        """
        # Construct token URL
        credentials = CLIENTID + ":" + CLIENTSECRET
        # Create signature
        signature = base64.b64encode(credentials.encode()).decode()
        # Construct Headers
        headers = {
            "Host": "api." + self.region + ".etd.cisco.com",
            "clientId": self.clientId,
            "secret": self.clientSecret,
            "x-api-key": self.apiKey,
            "Authorization": "Basic " + signature
        }
        tokenResponse = retryRequest(url=self.tokenUrl, headers=headers)
        if tokenResponse:
            if tokenResponse.status_code == HTTPStatus.OK:
                self.secretToken = tokenResponse.json().get('accessToken')
                return True
        return False

    def fetchMessage(self,nextPageToken=None):
        """
        Function to fetch messages from ETD message search api
        :param nextPageToken: token to fetch messages from next page, default value is None
        :return: messages fetched if successful, else empty dictionary
        """
        # Construct headers
        messageHeaders = {
            "Host": "api." + self.region + ".etd.cisco.com",
            "x-api-key": self.apiKey,
            "Accept": "application/json",
            "Authorization": "Bearer "+ self.secretToken
        }
        # Construct body
        messageJson = {
            "timestamp":[self.lastExecutedTime, self.currentUtcTime],
            "verdicts": self.messageFilter,
            "pageSize": PAGESIZE  #Each page will consist of PAGESIZE messages
        }
        # Append pageToken to body, if "nextPageToken" field contains value
        if nextPageToken:
            messageJson["pageToken"] = nextPageToken

        messageResponse = retryRequest(self.messageUrl, messageHeaders, messageJson)
        if messageResponse:
            if messageResponse.status_code == HTTPStatus.OK:
                logging.info("Message search API call successful")
                return messageResponse.json()
            elif messageResponse.status_code == HTTPStatus.UNAUTHORIZED:
                if not self.generateToken():
                    logging.error("Error in generating token for the request")
                    return {}
                messageHeaders["Authorization"] = "Bearer " + self.secretToken
                messageResponse = retryRequest(self.messageUrl, messageHeaders, messageJson)
                if messageResponse:
                    if messageResponse.status_code == HTTPStatus.OK:
                        logging.info("Message search API call successful")
                        return messageResponse.json()
                else:
                    return {}
            else:
                return {}
        else:
            logging.error("Message search API call failed")
            return {}

class Sentinel():
    """
    Class Sentinel is responsible for sending the messages to Log Analytics
    """
    @staticmethod
    def buildSignature(date, contentLength, method, contentType, resource):
        """
        Function to build signature for Authorization for Log Analytics Workspace
        :param date: current time in UTC
        :param contentLength: length of content
        :param method: http method (POST)
        :param contentType: type of content in payload(application/json)
        :param resource: endpoint for messages to be posted
        :return: computed authorization key
        """
        xHeaders = 'x-ms-date:' + date
        stringToHash = method + "\n" + str(contentLength) + "\n" + contentType + "\n" + xHeaders + "\n" + resource
        bytesToHash = bytes(stringToHash, encoding="utf-8")
        decodedKey = base64.b64decode(WORKSPACESHAREDKEY)
        encodedHash = base64.b64encode(hmac.new(decodedKey, bytesToHash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(WORKSPACEID, encodedHash)
        return authorization

    def sendMessagesToSentinel(self,etdMessages):
        """
        Function to batch messages received from ETD api
        :param etdMessages: Messages retrived from ETD api
        """
        messages = etdMessages.get("data").get("messages")
        for i in range(0, len(messages), CHUNKSIZE):
            batchedMessages = messages[i:i+CHUNKSIZE]
            self.postMessages(batchedMessages)

    def postMessages(self, body):
        """
        Function to post messages to log analytics
        :param body: payload body for post call
        """
        method = 'POST'
        contentType = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        contentLength = len(json.dumps(body))
        signature = self.buildSignature(rfc1123date, contentLength , method, contentType, resource)
        uri = "https://" + WORKSPACEID + ".ods.opinsights.azure.com" + resource + "?api-version=2016-04-01"
        headers = {
            'content-type': contentType,
            'Authorization': signature,
            'Log-Type': TABLENAME,
            'x-ms-date': rfc1123date
        }
        try:
            response = retryRequest(uri, headers, body)
        except Exception as err:
            logging.error("Error during sending logs to Azure Sentinel: {}".format(err))
        else:
            if response:
                if response.status_code == HTTPStatus.OK:
                    logging.info("Messages have been successfully sent to Azure Sentinel.")
                else:
                    logging.error("Error during sending messages to Azure Sentinel. Response code: {}".format(response.status_code))
            else:
                logging.error("Failed to post data to Azure Sentinel")

def setAndValidateEnvConfigurations():
    """
    Function to validate the environment variables set
    :return: True is all configurations are set, else False
    """
    missingConfigurations = []
    invalidVerdicts = []
    verdicts = ['spam', 'malicious', 'phishing', 'graymail', 'neutral', 'bec', 'scam', 'noVerdict']
    defaultValues = {"Region": "us", "Verdicts":"malicious"}
    requiredConfigurations = ['ApiKey', 'ClientId', 'ClientSecret', 'WorkspaceID', 'SharedKey', 'Region', 'Verdicts' ]
    for config in requiredConfigurations:
        if os.environ.get(config) is None or len(os.environ.get(config)) == 0:
            if config not in defaultValues:
                missingConfigurations.append(config)
            else:
                logging.error(f"Configuration is not set for {config}, using default value {defaultValues[config]}" )
        if os.environ.get(config) and config == "Verdicts":
            verdictList = os.environ.get(config).split(",")
            verdictList = [v.strip() for v in verdictList]
            for verdict in verdictList:
                if verdict not in verdicts:
                    invalidVerdicts.append(verdict)
    if invalidVerdicts:
        strOfVerdicts = ','.join([str(elem) for elem in invalidVerdicts]) 
        logging.error(f"Encountered invalid verdict, {strOfVerdicts}")
    if missingConfigurations:
        strOfConfig = ','.join([str(ele) for ele in missingConfigurations])
        logging.error(f"Please set the required configurations as environment variables {strOfConfig}")
        return False
    return True
       
def ciscoEtdConnector(last_timestamp_utc, next_timestamp_utc):
    """
    Entry point of the code, responsible for fetching ETD messages and post it to Microsoft Sentinel
    """
    # Check if env variables are configured
    if not setAndValidateEnvConfigurations():
        return
    # Create Sentinel class object
    sentinelObj = Sentinel()
    # Create ETD class object
    etdObj = ETD(APIKEY, CLIENTID, CLIENTSECRET, VERDICTS, REGION, last_timestamp_utc, next_timestamp_utc)
    nextPageToken = None
    #Generate Token for ETD api
    if not etdObj.generateToken():
        logging.error("Error in generating token for etd message search")          
        return
    while True:
        # Fetch messages from ETD
        etdMessages = etdObj.fetchMessage(nextPageToken)
        #  Check for pageToken in retrieved messages
        nextPageToken = etdMessages.get("nextPageToken")
        if not etdMessages.get("data") or not nextPageToken:
            break
        # Posting ETD messages to Sentinel
        sentinelObj.sendMessagesToSentinel(etdMessages)

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    # get last and next execution time
    last_timestamp_utc = mytimer.schedule_status[LAST].replace("+00:00", UTCZONE)
    next_timestamp_utc = mytimer.schedule_status[NEXT].replace("+00:00", UTCZONE)

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    ciscoEtdConnector(last_timestamp_utc, next_timestamp_utc)
