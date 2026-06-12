import requests
import logging
from typing import Optional, Any, Dict, List, Tuple
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


class SemperisAttackPaths:
    """Handles retrieval and transformation of Semperis attack paths."""

    @staticmethod
    def _get_headers(token: str) -> Dict[str, str]:
        """Build standard headers for Semperis API requests."""
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "curl/7.64.1",
        }

    @staticmethod
    def _fetch_attack_paths(token: str, endpoint: str) -> Optional[Dict[str, Any]]:
        """Fetch attack paths from Semperis API."""
        headers = SemperisAttackPaths._get_headers(token)
        payload = {}

        logger.info(f"Fetching attack paths from {endpoint}")

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
            attack_paths = data.get("AttackPaths", [])
            logger.info(f"Retrieved {len(attack_paths)} attack path records")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch attack paths: {e}")
            return None

    @staticmethod
    def _parse_node_info(node: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse node information into a flat dictionary."""
        if not node:
            return {}
        return {
            "id": node.get("id"),
            "type": node.get("type"),
            "label": node.get("label"),
            "domain": node.get("domain"),
            "oid": node.get("oid"),
        }

    @staticmethod
    def _transform_path_record(attack_path: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single attack path record for Azure ingestion."""
        target = SemperisAttackPaths._parse_node_info(attack_path.get("Target"))
        source = SemperisAttackPaths._parse_node_info(attack_path.get("Source"))
        path = attack_path.get("Path", {}) or {}

        return {
            "PathId": attack_path.get("Id"),
            "TargetId": target.get("id"),
            "TargetType": target.get("type"),
            "TargetLabel": target.get("label"),
            "TargetDomain": target.get("domain"),
            "TargetOID": target.get("oid"),
            "SourceId": source.get("id"),
            "SourceType": source.get("type"),
            "SourceLabel": source.get("label"),
            "SourceDomain": source.get("domain"),
            "SourceOID": source.get("oid"),
            "Cost": attack_path.get("Cost"),
            "RiskScore": attack_path.get("RiskScore"),
            "PathLength": len(path.get("nodes", []) or []),
            "Blowout": attack_path.get("Blowout"),
            "TimeGenerated": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _transform_paths(attack_paths_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform attack paths for Azure ingestion."""
        transformed = []
        for attack_path in attack_paths_data:
            record = SemperisAttackPaths._transform_path_record(attack_path)
            transformed.append(record)
        logger.info(f"Transformed {len(transformed)} attack path records")
        return transformed

    @staticmethod
    def _transform_link_record(path_id: str, link: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single attack path link record for Azure ingestion."""
        return {
            "PathId": path_id,
            "LinkId": link.get("id"),
            "SourceNodeId": link.get("source"),
            "TargetNodeId": link.get("target"),
            "LinkLabel": link.get("label"),
            "IdentitySource": link.get("IDS"),
            "TimeGenerated": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _transform_links(attack_paths_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform attack path links for Azure ingestion."""
        transformed = []
        for attack_path in attack_paths_data:
            path_id = attack_path.get("Id")
            path_obj = attack_path.get("Path", {}) or {}
            links = path_obj.get("links", []) or []

            for link in links:
                record = SemperisAttackPaths._transform_link_record(path_id, link)
                transformed.append(record)

        logger.info(f"Transformed {len(transformed)} attack path link records")
        return transformed

    @staticmethod
    def get_attack_paths(
        token: str,
        endpoint: str,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Retrieve and transform attack paths and links from Semperis API.
        
        Args:
            token: Semperis API authentication token
            endpoint: Attack paths API endpoint
            
        Returns:
            Tuple of (attack_paths_list, attack_path_links_list)
        """
        logger.info("Processing attack paths...")

        # Fetch attack paths data
        data = SemperisAttackPaths._fetch_attack_paths(token, endpoint)
        if not data:
            logger.warning("No attack paths data retrieved")
            return [], []

        # Extract attack paths list
        attack_paths_list = data.get("AttackPaths", [])
        if not attack_paths_list:
            logger.warning("No attack paths found in response")
            return [], []

        # Transform paths
        transformed_paths = SemperisAttackPaths._transform_paths(attack_paths_list)

        # Transform links
        transformed_links = SemperisAttackPaths._transform_links(attack_paths_list)

        logger.info(f"✓ Retrieved {len(transformed_paths)} attack paths and {len(transformed_links)} links from Semperis")
        return transformed_paths, transformed_links
