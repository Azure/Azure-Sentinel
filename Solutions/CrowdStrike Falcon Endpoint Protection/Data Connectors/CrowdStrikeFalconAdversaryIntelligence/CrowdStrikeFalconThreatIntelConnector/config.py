"""
Configuration module for CrowdStrike Falcon Adversary Intelligence Connector.
Handles loading and validation of environment variables.
"""

import os
import logging

# Constants
VERSION = "1.1.0"


class Config:
    """Configuration class to hold all environment variables and settings."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.crowdstrike_client_id = os.environ.get("CROWDSTRIKE_CLIENT_ID")
        self.crowdstrike_client_secret = os.environ.get("CROWDSTRIKE_CLIENT_SECRET")
        self.crowdstrike_base_url = os.environ.get("CROWDSTRIKE_BASE_URL")
        self.workspace_id = os.environ.get("WORKSPACE_ID")
        self.tenant_id = os.environ.get("TENANT_ID")
        self.indicators = os.environ.get("INDICATORS")
        self.aad_client_id = os.environ.get("AAD_CLIENT_ID")
        self.aad_client_secret = os.environ.get("AAD_CLIENT_SECRET")
        self.file_storage_connection_string = os.environ.get("FILE_STORAGE_CONNECTION_STRING")

        # Process look back days with validation
        try:
            self.look_back_days = int(os.environ.get("LOOK_BACK_DAYS", 1))
        except ValueError:
            look_back_value = os.environ.get("LOOK_BACK_DAYS")
            logging.error(
                "Invalid value for LOOK_BACK_DAYS environment variable: %s. "
                "Using default value of 1.",
                look_back_value
            )
            self.look_back_days = 1

        if self.look_back_days > 60:
            logging.warning(
                "Look back days is set to %s, which is more than 60 days. "
                "This may cause performance issues. Setting it to the maximum of 60 days.",
                self.look_back_days,
            )
            self.look_back_days = 60

        # Set user agent
        self.user_agent = f"microsoft-sentinel-ioc/{VERSION}"

    def validate_required_variables(self):
        """
        Validates that all required environment variables are set.

        Returns:
            bool: True if all required variables are set, False otherwise
        """
        required_vars = {
            "crowdstrike_client_id": "CrowdStrike API client ID",
            "crowdstrike_client_secret": "CrowdStrike API client secret",
            "crowdstrike_base_url": "CrowdStrike API base URL",
            "workspace_id": "Microsoft Sentinel workspace ID",
            "tenant_id": "Azure tenant ID",
            "aad_client_id": "Azure AD application client ID",
            "aad_client_secret": "Azure AD application client secret",
            "file_storage_connection_string": "Azure Storage connection string for state mgmt",
            "indicators": "Comma-separated list of indicator types to fetch"
        }

        missing_vars = []
        for var_name, var_description in required_vars.items():
            value = getattr(self, var_name)
            if not value or value.strip() == "":
                missing_vars.append(f"{var_name.upper()} ({var_description})")
                logging.error("Missing required environment variable: %s - %s",
                            var_name.upper(), var_description)

        if missing_vars:
            logging.error("Function cannot start due to missing environment variables:")
            for var in missing_vars:
                logging.error("  - %s", var)
            logging.error(
                "Please configure all required environment variables and restart the function."
            )
            return False

        logging.info("Environment variable validation passed. All required variables are set.")
        return True