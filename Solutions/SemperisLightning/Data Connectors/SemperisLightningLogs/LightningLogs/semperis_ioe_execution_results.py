import requests
import os
import logging
from typing import Optional, Any, Dict, List
from datetime import datetime, timezone, timedelta


logger = logging.getLogger(__name__)

TRIGGER_INTERVAL_HOURS = int(os.environ.get("TRIGGER_INTERVAL_HOURS", "1"))

class SemperisIOEExecutionResults:
    """Handles retrieval and transformation of Semperis IOE execution results."""

    @staticmethod
    def _get_headers(token: str) -> Dict[str, str]:
        """Build standard headers for Semperis API requests."""
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "curl/7.64.1",
        }

    @staticmethod
    def _get_time_filter() -> str:
        """Get the time filter for querying execution results.
        
        Uses CURRENT_GENERATED_TIME env var if set, otherwise calculates based on TRIGGER_INTERVAL_HOURS.
        Returns ISO8601 formatted timestamp with 'Z' suffix.
        """
        env_value = os.environ.get("CURRENT_GENERATED_TIME", "")

         
        if not env_value.strip():
            logger.info(f"CURRENT_GENERATED_TIME not set, using current UTC time minus {TRIGGER_INTERVAL_HOURS} hours")
            # Calculate time filter as current UTC time minus the trigger interval (hours).
            # This ensures we only fetch records that started after this calculated time.            
            current_time_dt = datetime.now(timezone.utc) - timedelta(hours=TRIGGER_INTERVAL_HOURS)
        else:
            logger.info(f"Using CURRENT_GENERATED_TIME from environment: {env_value}")
            # Parse ISO 8601 with optional 'Z'. If a date-only value is provided,
            # combine it with the current UTC time to produce a valid timestamp.
            if "T" not in env_value:
                date_only = datetime.strptime(env_value.strip(), "%Y-%m-%d").date()
                now_time = datetime.now(timezone.utc).time()
                current_time_dt = datetime.combine(date_only, now_time, tzinfo=timezone.utc)
            else:
                current_time_dt = datetime.fromisoformat(env_value.replace("Z", "+00:00"))
            logger.info(f"Parsed CURRENT_GENERATED_TIME as: {current_time_dt.isoformat()}")
            os.environ.pop("CURRENT_GENERATED_TIME", None)

        return current_time_dt.isoformat().replace("+00:00", "Z")

    @staticmethod
    def _fetch_executions(token: str, endpoint: str, time_filter: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch execution records from Semperis API."""
        headers = SemperisIOEExecutionResults._get_headers(token)
        params = {"$filter": f"StartTime gt {time_filter}"}

        logger.info(f"Fetching indicator executions with filter: {params['$filter']}")

        try:
            response = requests.get(
                endpoint,
                headers=headers,
                verify=False,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            executions = data.get("value", [])
            logger.info(f"Retrieved {len(executions)} execution records")
            return executions
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch executions: {e}")
            return None

    @staticmethod
    def _fetch_result_objects(
        token: str,
        executions_endpoint: str,
        execution_id: str,
    ) -> Optional[List[Dict[str, Any]]]:
        """Fetch result objects for a specific execution."""
        headers = SemperisIOEExecutionResults._get_headers(token)
        result_endpoint = executions_endpoint.rstrip('/') + '(' + execution_id + ')/IndicatorResultObjects'

        try:
            response = requests.get(
                result_endpoint,
                headers=headers,
                verify=False,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("value", [])
            logger.info(f"Retrieved {len(results)} result objects for execution {execution_id}")
            return results
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch results for execution {execution_id}: {e}")
            return None

    @staticmethod
    def _parse_object_values(object_values: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse ObjectValues array into a flat dictionary."""
        attrs: Dict[str, Any] = {}
        for ov in object_values:
            if isinstance(ov, dict):
                attr_name = ov.get("Attribute")
                attr_value = ov.get("Value")
                if attr_name is not None:
                    attrs[attr_name] = attr_value
        return attrs

    @staticmethod
    def _transform_result_record(
        indicator_id: str,
        execution_id: str,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform a single result record for Azure ingestion."""
        object_values = result.get("ObjectValues") or []
        attrs = SemperisIOEExecutionResults._parse_object_values(object_values)

        return {
            "IndicatorId": indicator_id,
            "ExecutionId": execution_id,
            "ObjectId": result.get("Id"),
            "DistinguishedName": attrs.get("DistinguishedName"),
            "PasswordPolicyDN": attrs.get("PasswordPolicyDistinguishedName"),
            "MinAge": attrs.get("MinAge"),
            "MaxAge": attrs.get("MaxAge"),
            "MinLength": attrs.get("MinLength"),
            "History": attrs.get("History"),
            "ComplexityEnabled": attrs.get("ComplexityEnabled"),
            "Ignored": attrs.get("Ignored"),
            "MFARegistered": attrs.get("MFARegistered"),
            "UserPrincipalName": attrs.get("UserPrincipalName"),
            "TimeGenerated": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _transform_results(
        indicator_id: str,
        execution_id: str,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Transform execution results for Azure ingestion."""
        transformed = []
        for result in results:
            record = SemperisIOEExecutionResults._transform_result_record(
                indicator_id,
                execution_id,
                result,
            )
            transformed.append(record)
        logger.info(f"Transformed {len(transformed)} result records")
        return transformed

    @staticmethod
    def get_indicator_execution_results(
        token: str,
        executions_endpoint: str,
    ) -> List[Dict[str, Any]]:
        """Retrieve and transform indicator execution results from Semperis API.
        
        Args:
            token: Semperis API authentication token
            executions_endpoint: Base endpoint for indicator executions
            
        Returns:
            List of transformed execution result records ready for Azure ingestion
        """
        logger.info("Processing indicator execution results...")

        # Get time filter
        time_filter = SemperisIOEExecutionResults._get_time_filter()

        # Fetch all executions
        executions = SemperisIOEExecutionResults._fetch_executions(
            token,
            executions_endpoint,
            time_filter,
        )

        if not executions:
            logger.warning("No executions found")
            return []

        # Process each execution and collect results
        all_results = []
        for execution in executions:
            execution_id = execution.get("IndicatorExecutionId")
            indicator_id = execution.get("IndicatorId")

            if not execution_id:
                logger.warning("Execution missing IndicatorExecutionId, skipping")
                continue

            logger.info(f"Processing execution {execution_id}")

            # Fetch result objects for this execution
            result_objects = SemperisIOEExecutionResults._fetch_result_objects(
                token,
                executions_endpoint,
                execution_id,
            )

            if result_objects:
                # Transform and collect
                transformed = SemperisIOEExecutionResults._transform_results(
                    indicator_id,
                    execution_id,
                    result_objects,
                )
                all_results.extend(transformed)

        logger.info(f"✓ Retrieved {len(all_results)} indicator execution result records from Semperis")
        return all_results
    
   
