import requests
import logging
from typing import Optional, Any, Dict, List
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


class SemperisTier0Nodes:
    """Handles retrieval and transformation of Semperis Tier0 nodes."""

    @staticmethod
    def _get_headers(token: str) -> Dict[str, str]:
        """Build standard headers for Semperis API requests."""
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "curl/7.64.1",
        }

    @staticmethod
    def _get_payload() -> Dict[str, Any]:
        """Build request payload for Tier0 nodes query."""
        return {
            "NumLayers": 0,
            "ZoneFilter": ["T0"],
        }

    @staticmethod
    def _fetch_nodes(token: str, endpoint: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch Tier 0 nodes from Semperis API."""
        headers = SemperisTier0Nodes._get_headers(token)
        payload = SemperisTier0Nodes._get_payload()

        logger.info(f"Fetching tier 0 nodes from {endpoint}")

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
            nodes = data.get("Data", {}).get("nodes", [])
            logger.info(f"Retrieved {len(nodes)} tier 0 node records")
            return nodes
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch tier 0 nodes: {e}")
            return None

    @staticmethod
    def _transform_node(node: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single node record for Azure ingestion."""
        return {
            "NodeId": node.get("id"),
            "NodeType": node.get("type"),
            "Label": node.get("label"),
            "Domain": node.get("domain"),
            "Zone": node.get("zone"),
            "IdentitySource": node.get("IDS"),
            "DN": node.get("DN"),
            "OID": node.get("oid"),
            "UserAccountControl": node.get("useraccountcontrol"),
            "PasswordLastSet": node.get("passwordlastset"),
            "WhenChanged": node.get("whenchanged"),
            "LastLogonTimestamp": node.get("lastlogontimestamp"),
            "IncomingEdgesOfConcern": node.get("totalIncomingEdgesOfConcern"),
            "UnclassifiedIncomingEdges": node.get("unClassifiedIncomingEdgesCount"),
            "TimeGenerated": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _transform_nodes(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform node records for Azure ingestion."""
        transformed = []
        for node in nodes:
            record = SemperisTier0Nodes._transform_node(node)
            transformed.append(record)
        logger.info(f"Transformed {len(transformed)} tier 0 node records")
        return transformed

    @staticmethod
    def get_tier_0_nodes(
        token: str,
        endpoint: str,
    ) -> List[Dict[str, Any]]:
        """Retrieve and transform Tier0 nodes from Semperis API.
        
        Args:
            token: Semperis API authentication token
            endpoint: Tier0 nodes API endpoint
            
        Returns:
            List of transformed node records ready for Azure ingestion
        """
        logger.info("Processing tier 0 nodes...")

        # Fetch nodes
        nodes = SemperisTier0Nodes._fetch_nodes(token, endpoint)
        if not nodes:
            logger.warning("No tier 0 nodes found")
            return []

        # Transform records
        transformed = SemperisTier0Nodes._transform_nodes(nodes)

        logger.info(f"✓ Retrieved {len(transformed)} tier 0 node records from Semperis")
        return transformed
