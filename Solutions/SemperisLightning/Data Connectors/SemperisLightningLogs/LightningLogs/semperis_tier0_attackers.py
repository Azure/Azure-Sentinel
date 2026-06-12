import requests
import logging
from typing import Optional, Any, Dict, List
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


class SemperisTier0Attackers:
    """Handles retrieval and transformation of Semperis Tier0 attackers."""

    @staticmethod
    def _get_headers(token: str) -> Dict[str, str]:
        """Build standard headers for Semperis API requests."""
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "curl/7.64.1",
        }

    @staticmethod
    def _fetch_attackers(token: str, endpoint: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch tier 0 attackers from Semperis API."""
        headers = SemperisTier0Attackers._get_headers(token)
        payload = {}

        logger.info(f"Fetching tier 0 attackers from {endpoint}")

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                verify=False,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            attackers = data if isinstance(data, list) else []
            logger.info(f"Retrieved {len(attackers)} attacker records")
            return attackers
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch tier 0 attackers: {e}")
            return None

    @staticmethod
    def _transform_object(domain_id: str, domain_name: str, domain_type: str, obj: Dict[str, Any], time_generated: str) -> Dict[str, Any]:
        """Transform a single attacker object record for Azure ingestion."""
        return {
            "DomainId": domain_id,
            "DomainName": domain_name,
            "DomainType": domain_type,
            "ObjectId": obj.get("Id"),
            "ObjectType": obj.get("Type"),
            "Zone": obj.get("Zone"),
            "DistinguishedName": obj.get("DistinguishedName"),
            "TimeGenerated": time_generated,
        }

    @staticmethod
    def _transform_objects(domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform attacker objects for Azure ingestion."""
        transformed = []
        time_generated = datetime.now(timezone.utc).isoformat()

        for domain in domains:
            domain_id = domain.get("Id")
            domain_name = domain.get("DomainName")
            domain_type = domain.get("DomainType")

            for obj in domain.get("Objects", []):
                record = SemperisTier0Attackers._transform_object(
                    domain_id,
                    domain_name,
                    domain_type,
                    obj,
                    time_generated,
                )
                transformed.append(record)

        logger.info(f"Transformed {len(transformed)} attacker records")
        return transformed

    @staticmethod
    def get_tier_0_attackers(
        token: str,
        endpoint: str,
    ) -> List[Dict[str, Any]]:
        """Retrieve and transform tier 0 attackers from Semperis API.
        
        Args:
            token: Semperis API authentication token
            endpoint: Tier0 attackers API endpoint
            
        Returns:
            List of transformed attacker records ready for Azure ingestion
        """
        logger.info("Processing tier 0 attackers...")

        # Fetch attackers
        attackers = SemperisTier0Attackers._fetch_attackers(token, endpoint)
        if not attackers:
            logger.warning("No tier 0 attackers found")
            return []

        # Transform records
        transformed = SemperisTier0Attackers._transform_objects(attackers)

        logger.info(f"✓ Retrieved {len(transformed)} tier 0 attacker records from Semperis")
        return transformed
   
   
