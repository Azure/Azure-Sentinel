"""This file contains all constants."""
import os
BASE_URL = os.environ.get("BaseURL")
ENDPOINTS = {
                "authentication": "auth/2/token",
                "get_lists": "account/2/get_lists",
                "add_integration_settings": "integration/1/settings/"
            }
LOGS_STARTS_WITH = "DataminrPulseAlerts:"
RELATEDALERTS_TABLE_NAME = "{}_relatedAlerts"
VULNERABILITY_PRODUCTS_TABLE_NAME = "{}_vulnerabilities_products"
VULNERABILITY_PRODUCTS_RELATEDALERTS_TABLE_NAME = "{}_vulnerabilities_products_relatedAlerts"
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL = os.environ.get("LogLevel", "")
