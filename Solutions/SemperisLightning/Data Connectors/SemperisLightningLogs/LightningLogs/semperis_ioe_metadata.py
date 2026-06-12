import requests
import logging
import json
from typing import Optional, Any, Dict, List
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


class SemperisIOEMetadata:
    """Handles retrieval and transformation of Semperis IOE metadata."""

    @staticmethod
    def _get_headers(token: str) -> Dict[str, str]:
        """Build standard headers for Semperis API requests."""
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "curl/7.64.1",
        }

    @staticmethod
    def _fetch_metadata(token: str, endpoint: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch indicator metadata records from Semperis API."""
        headers = SemperisIOEMetadata._get_headers(token)

        logger.info(f"Fetching indicator metadata from {endpoint}")

        try:
            response = requests.get(
                endpoint,
                headers=headers,
                verify=False,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            metadata = data.get("value", [])
            logger.info(f"Retrieved {len(metadata)} indicator metadata records")
            return metadata
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch indicator metadata: {e}")
            return None

    @staticmethod
    def _parse_list_to_string(items: Any) -> str:
        """Convert a list or single value to a comma-separated string."""
        if isinstance(items, list):
            return ",".join(str(item) for item in items)
        elif items is not None:
            return str(items)
        return ""

    @staticmethod
    def _extract_mitre_tags(security_framework_tags: List[Dict[str, Any]]) -> str:
        """Extract MITRE ATT&CK tags from security framework tags."""
        mitre_tags: List[str] = []

        for framework in security_framework_tags or []:
            if not isinstance(framework, dict):
                continue

            if framework.get("FrameworkName") == "MITRE ATT&CK":
                tags = framework.get("Tags") or []
                if isinstance(tags, list):
                    mitre_tags.extend(str(t) for t in tags)
                else:
                    mitre_tags.append(str(tags))

        return ",".join(sorted(set(mitre_tags))) if mitre_tags else ""

    @staticmethod
    def _transform_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single metadata record for Azure ingestion."""
        directory_types = record.get("DirectoryTypes") or []
        packages = record.get("Packages") or []
        security_framework_tags = record.get("SecurityFrameworkTags") or []
        permissions = record.get("Permissions") or []

        # Extract MITRE tags
        mitre_tags_str = SemperisIOEMetadata._extract_mitre_tags(security_framework_tags)

        return {
            "IndicatorId": record.get("IndicatorId"),
            "Name": record.get("Name"),
            "Severity": record.get("Severity"),
            "CategoryName": record.get("CategoryName"),
            "Weight": record.get("Weight"),
            "Schedule": record.get("Schedule"),
            "Version": record.get("Version"),
            "DirectoryTypes": SemperisIOEMetadata._parse_list_to_string(directory_types),
            "Description": record.get("Description"),
            "LoC": record.get("LoC"),
            "Remediation": record.get("Remediation"),
            "DateAdded": record.get("DateAdded"),
            "Packages": SemperisIOEMetadata._parse_list_to_string(packages),
            "SecurityFrameworkTags": json.dumps(security_framework_tags),
            "Permissions": json.dumps(permissions),
            "MitreAttackTags": mitre_tags_str,
            "TimeGenerated": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _transform_records(metadata_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform metadata records for Azure ingestion."""
        transformed = []
        for record in metadata_list:
            transformed_record = SemperisIOEMetadata._transform_record(record)
            transformed.append(transformed_record)
        logger.info(f"Transformed {len(transformed)} metadata records")
        return transformed

    @staticmethod
    def get_indicator_metadata(
        token: str,
        endpoint: str,
    ) -> List[Dict[str, Any]]:
        """Retrieve and transform indicator metadata from Semperis API.
        
        Args:
            token: Semperis API authentication token
            endpoint: Indicator metadata API endpoint
            
        Returns:
            List of transformed metadata records ready for Azure ingestion
        """
        logger.info("Processing indicator metadata...")

        # Fetch metadata
        metadata = SemperisIOEMetadata._fetch_metadata(token, endpoint)
        if not metadata:
            logger.warning("No indicator metadata found")
            return []

        # Transform records
        transformed = SemperisIOEMetadata._transform_records(metadata)

        logger.info(f"✓ Retrieved {len(transformed)} indicator metadata records from Semperis")
        return transformed