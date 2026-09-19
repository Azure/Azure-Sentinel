from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Any, Iterable
from urllib.parse import quote

import requests
from azure.identity import DefaultAzureCredential

from .contract import Contract

ARM_SCOPE = "https://management.azure.com/.default"
INGESTION_SCOPE = "https://monitor.azure.com/.default"
LOG_ANALYTICS_SCOPE = "https://api.loganalytics.io/.default"
ARM_BASE = "https://management.azure.com"
RESOURCE_GRAPH_API = "2021-03-01"
DCE_API = "2023-03-11"
DCR_API = "2023-03-11"
TABLE_API = "2022-10-01"
INGESTION_API = "2023-01-01"
ROLE_ASSIGNMENT_API = "2022-04-01"
MONITORING_METRICS_PUBLISHER_ROLE_GUID = "3913510d-42f4-4e42-8a64-420c390055eb"
MANAGED_BY = "azure-monitor-logs-ingestion"


class AzureRequestError(RuntimeError):
    def __init__(self, method: str, url: str, status: int, body: str):
        self.method = method
        self.url = url
        self.status = status
        self.body = body
        super().__init__(f"{method} {url} failed with HTTP {status}: {body[:2000]}")


@dataclass(frozen=True)
class Workspace:
    id: str
    name: str
    subscription_id: str
    resource_group: str
    location: str
    customer_id: str


@dataclass(frozen=True)
class ProvisionedResources:
    workspace: Workspace
    dce_id: str
    dce_endpoint: str
    dcr_id: str
    dcr_immutable_id: str

    def as_dict(self) -> dict[str, str]:
        return {
            "workspaceId": self.workspace.id,
            "workspaceCustomerId": self.workspace.customer_id,
            "dceId": self.dce_id,
            "dceEndpoint": self.dce_endpoint,
            "dcrId": self.dcr_id,
            "dcrImmutableId": self.dcr_immutable_id,
        }


class AzureClient:
    def __init__(
        self,
        credential: Any | None = None,
        session: requests.Session | None = None,
        retries: int = 4,
    ):
        self.credential = credential or DefaultAzureCredential(
            exclude_interactive_browser_credential=True
        )
        self.session = session or requests.Session()
        self.retries = retries
        self._tokens: dict[str, str] = {}

    def _token(self, scope: str) -> str:
        if scope not in self._tokens:
            self._tokens[scope] = self.credential.get_token(scope).token
        return self._tokens[scope]

    def request(
        self,
        method: str,
        url: str,
        *,
        scope: str = ARM_SCOPE,
        json_body: Any | None = None,
        expected: Iterable[int] = (200,),
    ) -> requests.Response:
        for attempt in range(self.retries + 1):
            response = self.session.request(
                method,
                url,
                headers={
                    "Authorization": f"Bearer {self._token(scope)}",
                    "Content-Type": "application/json",
                },
                json=json_body,
                timeout=60,
            )
            if response.status_code in expected:
                return response
            if response.status_code not in {408, 429, 500, 502, 503, 504}:
                raise AzureRequestError(method, url, response.status_code, response.text)
            if attempt == self.retries:
                raise AzureRequestError(method, url, response.status_code, response.text)
            retry_after = response.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else min(2**attempt, 8)
            time.sleep(delay)
        raise AssertionError("unreachable")

    def resource_graph(self, query: str) -> list[dict[str, Any]]:
        url = f"{ARM_BASE}/providers/Microsoft.ResourceGraph/resources?api-version={RESOURCE_GRAPH_API}"
        response = self.request(
            "POST",
            url,
            json_body={"query": query, "options": {"resultFormat": "objectArray"}},
        )
        return response.json().get("data", [])

    def resolve_workspace(self, identifier: str) -> Workspace:
        escaped = identifier.replace("'", "''")
        if identifier.lower().startswith("/subscriptions/"):
            query = (
                "Resources "
                "| where type =~ 'microsoft.operationalinsights/workspaces' "
                f"| where id =~ '{escaped}' "
                "| project id, name, subscriptionId, resourceGroup, location, "
                "customerId=tostring(properties.customerId)"
            )
        else:
            query = (
                "Resources "
                "| where type =~ 'microsoft.operationalinsights/workspaces' "
                f"| where name =~ '{escaped}' or tostring(properties.customerId) =~ '{escaped}' "
                "| project id, name, subscriptionId, resourceGroup, location, "
                "customerId=tostring(properties.customerId)"
            )
        rows = self.resource_graph(query)
        if not rows:
            raise RuntimeError(f"Log Analytics workspace {identifier!r} was not found")
        if len(rows) > 1:
            ids = ", ".join(row["id"] for row in rows)
            raise RuntimeError(
                f"workspace {identifier!r} is ambiguous; use its ARM ID. Matches: {ids}"
            )
        row = rows[0]
        return Workspace(
            id=row["id"],
            name=row["name"],
            subscription_id=row["subscriptionId"],
            resource_group=row["resourceGroup"],
            location=row["location"],
            customer_id=row.get("customerId", ""),
        )

    def _resource_url(self, resource_id: str, api_version: str) -> str:
        return f"{ARM_BASE}{resource_id}?api-version={api_version}"

    def _put_resource(
        self, resource_id: str, api_version: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        response = self.request(
            "PUT",
            self._resource_url(resource_id, api_version),
            json_body=body,
            expected=(200, 201, 202),
        )
        if response.status_code == 202:
            operation_url = response.headers.get("Azure-AsyncOperation") or response.headers.get(
                "Location"
            )
            if operation_url:
                self._wait_for_operation(operation_url)
            response = self.request(
                "GET",
                self._resource_url(resource_id, api_version),
                expected=(200,),
            )
        return response.json()

    def _put_managed_resource(
        self, resource_id: str, api_version: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        existing = self.request(
            "GET",
            self._resource_url(resource_id, api_version),
            expected=(200, 404),
        )
        if existing.status_code == 200:
            tags = existing.json().get("tags", {}) or {}
            if tags.get("managed-by") != MANAGED_BY:
                raise RuntimeError(
                    f"resource {resource_id!r} already exists but is not managed by "
                    f"this tool; choose a different resource name"
                )
        return self._put_resource(resource_id, api_version, body)

    def _wait_for_operation(self, url: str, attempts: int = 60) -> None:
        for _ in range(attempts):
            response = self.request("GET", url, expected=(200, 201, 202, 204))
            if response.status_code == 204:
                return
            body = response.json() if response.content else {}
            status = str(body.get("status", "")).lower()
            if status in {"succeeded", "completed"}:
                return
            if status in {"failed", "canceled", "cancelled"}:
                raise RuntimeError(f"Azure operation failed: {json.dumps(body)}")
            time.sleep(2)
        raise RuntimeError("Azure operation did not complete within 120 seconds")

    def _resource_ids(
        self, workspace: Workspace, contract: Contract
    ) -> tuple[str, str]:
        prefix = (
            f"/subscriptions/{workspace.subscription_id}"
            f"/resourceGroups/{workspace.resource_group}"
            "/providers/Microsoft.Insights"
        )
        return (
            f"{prefix}/dataCollectionEndpoints/{contract.resources.dce}",
            f"{prefix}/dataCollectionRules/{contract.resources.dcr}",
        )

    def ensure_destination_table(
        self, workspace: Workspace, contract: Contract
    ) -> dict[str, Any]:
        table_id = (
            f"{workspace.id}/tables/{contract.destination.table}"
        )
        url = self._resource_url(table_id, TABLE_API)
        response = self.request("GET", url, expected=(200, 404))
        if contract.destination.kind == "standard":
            if response.status_code == 404:
                raise RuntimeError(
                    f"standard table {contract.destination.table!r} is not registered "
                    f"in workspace {workspace.name!r}"
                )
            return response.json()
        requested_columns = [
            column.as_dict() for column in contract.destination.columns
        ]
        if response.status_code == 200:
            schema = response.json().get("properties", {}).get("schema", {}) or {}
            existing_columns = schema.get("columns", []) or []
            existing_by_name = {
                str(column.get("name", "")).lower(): column
                for column in existing_columns
            }
            for column in requested_columns:
                existing = existing_by_name.get(column["name"].lower())
                if existing and str(existing.get("type", "")).lower() != column["type"]:
                    raise RuntimeError(
                        f"custom table column {column['name']!r} already has type "
                        f"{existing.get('type')!r}, not {column['type']!r}"
                    )
                if not existing:
                    existing_columns.append(column)
            requested_columns = existing_columns
        return self._put_resource(
            table_id,
            TABLE_API,
            {
                "properties": {
                    "schema": {
                        "name": contract.destination.table,
                        "columns": requested_columns,
                    }
                }
            },
        )

    @staticmethod
    def _merge_dcr_body(
        existing: dict[str, Any],
        body: dict[str, Any],
        input_stream: str,
        workspace_id: str,
    ) -> dict[str, Any]:
        merged = json.loads(json.dumps(existing))
        merged.pop("id", None)
        merged.pop("name", None)
        merged.pop("type", None)
        merged.pop("etag", None)
        merged["location"] = body["location"]
        merged["kind"] = body["kind"]
        merged["tags"] = {
            **(existing.get("tags", {}) or {}),
            **body["tags"],
        }

        properties = merged.setdefault("properties", {})
        requested = body["properties"]
        existing_endpoint = properties.get("dataCollectionEndpointId")
        if existing_endpoint and existing_endpoint.lower() != requested[
            "dataCollectionEndpointId"
        ].lower():
            raise RuntimeError(
                "existing managed DCR uses a different data collection endpoint"
            )
        properties["dataCollectionEndpointId"] = requested[
            "dataCollectionEndpointId"
        ]

        destinations = properties.setdefault("destinations", {})
        log_analytics = destinations.setdefault("logAnalytics", [])
        destination = next(
            (
                item
                for item in log_analytics
                if str(item.get("workspaceResourceId", "")).lower()
                == workspace_id.lower()
            ),
            None,
        )
        if destination is None:
            raise RuntimeError(
                "existing managed DCR does not target the requested workspace"
            )
        destination_name = destination["name"]

        stream_declarations = properties.setdefault("streamDeclarations", {})
        stream_declarations[input_stream] = requested["streamDeclarations"][
            input_stream
        ]
        data_flows = properties.setdefault("dataFlows", [])
        properties["dataFlows"] = [
            flow
            for flow in data_flows
            if input_stream not in (flow.get("streams", []) or [])
        ]
        new_flow = requested["dataFlows"][0]
        new_flow["destinations"] = [destination_name]
        properties["dataFlows"].append(new_flow)
        return merged

    def provision(self, contract: Contract) -> ProvisionedResources:
        workspace = self.resolve_workspace(contract.workspace)
        location = contract.location or workspace.location
        self.ensure_destination_table(workspace, contract)
        dce_id, dcr_id = self._resource_ids(workspace, contract)
        dce = self._put_managed_resource(
            dce_id,
            DCE_API,
            {
                "location": location,
                "properties": {
                    "networkAcls": {"publicNetworkAccess": "Enabled"}
                },
                "tags": {"managed-by": MANAGED_BY},
            },
        )
        dcr_body = {
            "location": location,
            "kind": "Direct",
            "properties": {
                "dataCollectionEndpointId": dce_id,
                "streamDeclarations": {
                    contract.input_stream: {
                        "columns": [
                            column.as_dict() for column in contract.input_columns
                        ]
                    }
                },
                "destinations": {
                    "logAnalytics": [
                        {
                            "name": "destination",
                            "workspaceResourceId": workspace.id,
                        }
                    ]
                },
                "dataFlows": [
                    {
                        "streams": [contract.input_stream],
                        "destinations": ["destination"],
                        "transformKql": contract.transform_kql,
                        "outputStream": contract.destination.output_stream,
                    }
                ],
            },
            "tags": {"managed-by": MANAGED_BY},
        }
        existing_dcr = self.request(
            "GET",
            self._resource_url(dcr_id, DCR_API),
            expected=(200, 404),
        )
        if existing_dcr.status_code == 200:
            existing_value = existing_dcr.json()
            tags = existing_value.get("tags", {}) or {}
            if tags.get("managed-by") != MANAGED_BY:
                raise RuntimeError(
                    f"resource {dcr_id!r} already exists but is not managed by "
                    f"this tool; choose a different resource name"
                )
            dcr_body = self._merge_dcr_body(
                existing_value,
                dcr_body,
                contract.input_stream,
                workspace.id,
            )
            dcr = self._put_resource(dcr_id, DCR_API, dcr_body)
        else:
            dcr = self._put_resource(dcr_id, DCR_API, dcr_body)
        endpoint = dce.get("properties", {}).get("logsIngestion", {}).get("endpoint")
        immutable_id = dcr.get("properties", {}).get("immutableId")
        if not endpoint or not immutable_id:
            raise RuntimeError("Azure did not return the DCE endpoint or DCR immutable ID")
        return ProvisionedResources(
            workspace=workspace,
            dce_id=dce_id,
            dce_endpoint=endpoint,
            dcr_id=dcr_id,
            dcr_immutable_id=immutable_id,
        )

    def get_resources(self, contract: Contract) -> ProvisionedResources:
        workspace = self.resolve_workspace(contract.workspace)
        dce_id, dcr_id = self._resource_ids(workspace, contract)
        dce = self.request(
            "GET", self._resource_url(dce_id, DCE_API), expected=(200,)
        ).json()
        dcr = self.request(
            "GET", self._resource_url(dcr_id, DCR_API), expected=(200,)
        ).json()
        endpoint = dce.get("properties", {}).get("logsIngestion", {}).get("endpoint")
        immutable_id = dcr.get("properties", {}).get("immutableId")
        if not endpoint or not immutable_id:
            raise RuntimeError("existing DCE/DCR is missing ingestion properties")
        return ProvisionedResources(
            workspace=workspace,
            dce_id=dce_id,
            dce_endpoint=endpoint,
            dcr_id=dcr_id,
            dcr_immutable_id=immutable_id,
        )

    def authorize(
        self,
        dcr_id: str,
        principal_id: str,
        principal_type: str = "ServicePrincipal",
    ) -> str:
        parts = dcr_id.split("/")
        try:
            subscription_id = parts[parts.index("subscriptions") + 1]
        except (ValueError, IndexError) as exc:
            raise ValueError(f"invalid DCR resource ID: {dcr_id!r}") from exc
        role_definition_id = (
            f"/subscriptions/{subscription_id}"
            "/providers/Microsoft.Authorization/roleDefinitions/"
            f"{MONITORING_METRICS_PUBLISHER_ROLE_GUID}"
        )
        assignment_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"{dcr_id.lower()}:{principal_id.lower()}:monitoring-metrics-publisher",
            )
        )
        resource_id = (
            f"{dcr_id}/providers/Microsoft.Authorization/roleAssignments/{assignment_id}"
        )
        self._put_resource(
            resource_id,
            ROLE_ASSIGNMENT_API,
            {
                "properties": {
                    "principalId": principal_id,
                    "roleDefinitionId": role_definition_id,
                    "principalType": principal_type,
                }
            },
        )
        return resource_id

    @staticmethod
    def batches(
        records: list[dict[str, Any]],
        max_records: int = 500,
        max_bytes: int = 900_000,
    ) -> list[list[dict[str, Any]]]:
        batches: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        current_size = 2
        for record in records:
            encoded_size = len(
                json.dumps(record, separators=(",", ":"), ensure_ascii=False).encode(
                    "utf-8"
                )
            )
            if encoded_size + 2 > max_bytes:
                raise ValueError(
                    f"a single record is {encoded_size} bytes, exceeding the "
                    f"{max_bytes}-byte batch limit"
                )
            separator_size = 1 if current else 0
            if current and (
                len(current) >= max_records
                or current_size + separator_size + encoded_size > max_bytes
            ):
                batches.append(current)
                current = []
                current_size = 2
                separator_size = 0
            current.append(record)
            current_size += separator_size + encoded_size
        if current:
            batches.append(current)
        return batches

    def ingest(
        self,
        contract: Contract,
        resources: ProvisionedResources,
        records: list[dict[str, Any]],
        *,
        max_records: int = 500,
        max_bytes: int = 900_000,
    ) -> dict[str, Any]:
        batches = self.batches(records, max_records=max_records, max_bytes=max_bytes)
        encoded_stream = quote(contract.input_stream, safe="-_")
        url = (
            f"{resources.dce_endpoint}/dataCollectionRules/"
            f"{resources.dcr_immutable_id}/streams/{encoded_stream}"
            f"?api-version={INGESTION_API}"
        )
        for batch in batches:
            self.request(
                "POST",
                url,
                scope=INGESTION_SCOPE,
                json_body=batch,
                expected=(200, 202, 204),
            )
        return {"recordsAccepted": len(records), "batchesAccepted": len(batches)}

    def verify(
        self, resources: ProvisionedResources, table: str, lookback_minutes: int
    ) -> dict[str, Any]:
        if not resources.workspace.customer_id:
            raise RuntimeError("workspace customer ID is unavailable for verification")
        query = (
            f"{table}\n"
            f"| where ingestion_time() >= ago({lookback_minutes}m)\n"
            "| summarize Rows=count(), FirstIngested=min(ingestion_time()), "
            "LastIngested=max(ingestion_time())"
        )
        url = (
            "https://api.loganalytics.azure.com/v1/workspaces/"
            f"{resources.workspace.customer_id}/query"
        )
        response = self.request(
            "POST",
            url,
            scope=LOG_ANALYTICS_SCOPE,
            json_body={"query": query},
            expected=(200,),
        ).json()
        tables = response.get("tables", [])
        rows = tables[0].get("rows", []) if tables else []
        columns = tables[0].get("columns", []) if tables else []
        result = dict(zip((column["name"] for column in columns), rows[0])) if rows else {}
        fresh_rows = int(result.get("Rows") or 0)
        return {
            "query": query,
            "result": result,
            "freshRows": fresh_rows,
            "found": fresh_rows > 0,
        }
