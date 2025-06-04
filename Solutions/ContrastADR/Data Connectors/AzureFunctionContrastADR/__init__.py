import json
import logging
import os
import datetime
import time
import requests
import base64
import hashlib
import hmac
import azure.functions as func

def retry(retry_times, retry_interval):
    """A decorator to retry a function/method upon failure."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, retry_times + 1):
                try:
                    logging.info(f"Attempt {attempt} for {func.__name__}.")
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.error(f"Attempt {attempt} failed: {e}")
                    if attempt < retry_times:
                        logging.info(f"Retrying in {retry_interval} seconds...")
                        time.sleep(retry_interval)
                    else:
                        logging.error(f"All {retry_times} attempts failed.")
                        raise

        return wrapper
    
    return decorator


class Config:
    """Handles configuration settings."""

    @staticmethod
    def get_env_variable(key: str, default=None):
        value = os.getenv(key)
        if not value and default is None:
            logging.error(f"Environment variable {key} is not set.")
            raise ValueError(f"Missing environment variable: {key}")
        return value or default

class SentinelLogger:
    """Handles sending logs to Microsoft Sentinel Log Analytics workspace."""

    def __init__(self):
        self.workspace_id = Config.get_env_variable("WORKSPACE_ID")
        self.shared_key = Config.get_env_variable("SHARED_KEY")
        self.log_type = Config.get_env_variable("LOG_TYPE", "ContrastADR")
        self.retry_times = int(Config.get_env_variable("RETRY_TIMES", 3))
        self.retry_interval = int(Config.get_env_variable("RETRY_INTERVAL", 10))

    def build_signature(self, date, content_length, method, content_type, resource):
        x_headers = f"x-ms-date:{date}"
        string_to_hash = (
            f"{method}\n{content_length}\n{content_type}\n{x_headers}\n{resource}"
        )
        bytes_to_hash = string_to_hash.encode("utf-8")
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = hmac.new(
            decoded_key, bytes_to_hash, digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(encoded_hash).decode()


    @retry(
        retry_times=int(Config.get_env_variable("RETRY_TIMES", 3)),
        retry_interval=int(Config.get_env_variable("RETRY_INTERVAL", 10)),
    )
    def send_logs(self, log_data):
        log_data_json = json.dumps(log_data)
        resource = f"/api/logs"
        content_type = "application/json"
        rfc1123_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        content_length = len(log_data_json)
        signature = self.build_signature(
            rfc1123_date, content_length, "POST", content_type, resource
        )
        uri = f"https://{self.workspace_id}.ods.opinsights.azure.com{resource}?api-version=2016-04-01"
        headers = {
            "Content-Type": content_type,
            "Authorization": f"SharedKey {self.workspace_id}:{signature}",
            "Log-Type": self.log_type,
            "x-ms-date": rfc1123_date,
        }

        logging.info("Sending log data to Sentinel.")
        response = requests.post(uri, headers=headers, data=log_data_json)
        response.raise_for_status()
        logging.info("Log successfully sent to Sentinel.")

class DataProcessor:
    """Handles data processing tasks such as excluding fields."""

    @staticmethod
    def exclude_fields(data, excluded_fields):
        if isinstance(data, dict):
            sanitized_data = {}
            for key, value in data.items():
                if key not in excluded_fields:
                    # Check for nested exclusions using dot notation
                    nested_exclusions = [
                        field[len(key) + 1 :]
                        for field in excluded_fields
                        if field.startswith(f"{key}.")
                    ]
                    sanitized_data[key] = DataProcessor.exclude_fields(
                        value, nested_exclusions
                    )
                else:
                    logging.info(f"Excluded field: {key}")
            return sanitized_data
        elif isinstance(data, list):
            return [
                DataProcessor.exclude_fields(item, excluded_fields) for item in data
            ]
        return data


class ADRHandler:
    """Handles processing of ADR events."""

    def __init__(self, req_body):
        self.req_body = req_body
        self.base_url = "https://teamserver-scantest.contsec.com"
        self.endpoint_template = "/api/v4/organizations/{org_uuid}/applications/{app_uuid}/attack-events/{event_uuid}"
        self.excluded_fields = [
            field.strip()
            for field in Config.get_env_variable("EXCLUDED_FIELDS", "").split(",")
            if field.strip()
        ]
        self.retry_times = int(Config.get_env_variable("RETRY_TIMES", 3))
        self.retry_interval = int(Config.get_env_variable("RETRY_INTERVAL", 10))
        
    @retry(
        retry_times=int(Config.get_env_variable("RETRY_TIMES", 3)),
        retry_interval=int(Config.get_env_variable("RETRY_INTERVAL", 10)),
    )
    def enrich_data(self, attack_event_uuid, application_uuid,organization_uuid):
        endpoint = self.endpoint_template.format(
            org_uuid=organization_uuid,
            app_uuid=application_uuid,
            event_uuid=attack_event_uuid,
        )

        username= Config.get_env_variable("CONTRAST_USER_NAME")
        service_key=Config.get_env_variable("CONTRAST_SERVICE_KEY")
        api_key=Config.get_env_variable("CONTRAST_API_KEY")

        encoded_credentials = base64.b64encode(
            f"{username}:{service_key}".encode()
        ).decode()

        headers = {
            "Authorization": f"{encoded_credentials}",
            "Api-key": api_key,
            "Accept":"application/json"
        }

        full_url = f"{self.base_url}{endpoint}"
        timeout = int(Config.get_env_variable("TIMEOUT"))
        response = requests.get(full_url, timeout=timeout, headers=headers)
        response.raise_for_status()
        return response.json()

    def process_request(self):
        attack_event_uuid, application_uuid,organization_uuid= self.validate_request()
        enrichment_enabled = os.getenv("ENRICHMENT_DATA_SUBSCRIPTION") == "TRUE"
        current_epoch = int(time.time())*1000
        self.req_body["detectedTime"] = str(datetime.datetime.utcfromtimestamp(int(self.req_body.get("detectedTime", current_epoch))/1000))

        if enrichment_enabled:
            try:
                response_data = self.enrich_data(attack_event_uuid, application_uuid,organization_uuid)
                self.req_body["request"] = response_data.get("request")
                self.req_body["codeLocation"] = response_data.get("codeLocation")
                self.req_body["vectorAnalysis"] = response_data.get("vectorAnalysis")

               
            except Exception as e:
                # Fallback to using webhook data
                logging.error(f"Enrichment API call failed: {e}")
                response_data = self.req_body
        return DataProcessor.exclude_fields(self.req_body, self.excluded_fields)

    def validate_request(self):
        attack_event_uuid = self.req_body.get("eventUuid")
        application_uuid = self.req_body.get("application", {}).get("id")
        organization_uuid = self.req_body.get("organizationUuid")
        

        if not attack_event_uuid or not application_uuid or not organization_uuid:
            raise ValueError("Missing required fields in JSON payload")

        return attack_event_uuid, application_uuid,organization_uuid


# Azure Function Definition
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        # Parse request body
        try:
            req_body = req.get_json()
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON payload: {e}")
            return func.HttpResponse("Invalid JSON payload", status_code=400)

        adr_handler = ADRHandler(req_body)
        sanitized_response = adr_handler.process_request()

        # send data to sentinel
        sentinel_logger = SentinelLogger()
        try:
            sentinel_logger.send_logs(sanitized_response)
        except Exception as e:
            logging.error(f"Failed to send logs to Sentinel after retries: {e}")

        return func.HttpResponse(
            json.dumps(sanitized_response),
            status_code=200,
            mimetype="application/json",
        )
    except ValueError as ve:
        logging.error(f"Validation error: {ve}")
        return func.HttpResponse(str(ve), status_code=400)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return func.HttpResponse(
            "An error occurred while processing the request", status_code=500
        )
