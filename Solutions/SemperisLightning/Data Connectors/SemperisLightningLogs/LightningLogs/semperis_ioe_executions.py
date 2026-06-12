import requests
import logging
from typing import Optional, Any, Dict, List
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


class SemperisIOEExecutions:
    """Handles retrieval and transformation of Semperis IOE executions."""

    @staticmethod
    def _get_headers(token: str) -> Dict[str, str]:
        """Build standard headers for Semperis API requests."""
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "curl/7.64.1",
        }

    @staticmethod
    def _fetch_executions(token: str, endpoint: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch indicator execution records from Semperis API."""
        headers = SemperisIOEExecutions._get_headers(token)

        logger.info(f"Fetching indicator executions from {endpoint}")

        try:
            response = requests.get(
                endpoint,
                headers=headers,
                verify=False,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            executions = data.get("value", [])
            logger.info(f"Retrieved {len(executions)} indicator execution records")
            return executions
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch indicator executions: {e}")
            return None

    @staticmethod
    def _transform_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single execution record for Azure ingestion."""
        return {
            **record,
            "TimeGenerated": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _transform_records(executions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform execution records for Azure ingestion."""
        transformed = []
        for execution in executions:
            record = SemperisIOEExecutions._transform_record(execution)
            transformed.append(record)
        logger.info(f"Transformed {len(transformed)} execution records")
        return transformed

    @staticmethod
    def get_indicator_executions(
        token: str,
        endpoint: str,
    ) -> List[Dict[str, Any]]:
        """Retrieve and transform indicator executions from Semperis API.
        
        Args:
            token: Semperis API authentication token
            endpoint: Indicator executions API endpoint
            
        Returns:
            List of transformed execution records ready for Azure ingestion
        """
        logger.info("Processing indicator executions...")

        # Fetch executions
        executions = SemperisIOEExecutions._fetch_executions(token, endpoint)
        if not executions:
            logger.warning("No indicator executions found")
            return []

        # Transform records
        transformed = SemperisIOEExecutions._transform_records(executions)

        logger.info(f"✓ Retrieved {len(transformed)} indicator execution records from Semperis")
        return transformed
   
   
