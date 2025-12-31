# NetworkAccessTraffic

Reference for NetworkAccessTraffic table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | IT & Management Tools, Network, Security |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/networkaccesstraffic) |

## Solutions (2)

This table is used by the following solutions:

- [Global Secure Access](../solutions/global-secure-access.md)
- [Microsoft Entra ID](../solutions/microsoft-entra-id.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Entra ID](../connectors/azureactivedirectory.md)

---

## Content Items Using This Table (6)

### Analytic Rules (4)

**In solution [Global Secure Access](../solutions/global-secure-access.md):**
- [GSA - Detect Abnormal Deny Rate for Source to Destination IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Analytic%20Rules/SWG%20-%20Abnormal%20Deny%20Rate.yaml)
- [GSA - Detect Connections Outside Operational Hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Analytic%20Rules/Identity%20-%20AfterHoursActivity.yaml)
- [GSA - Detect Protocol Changes for Destination Ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Analytic%20Rules/SWG%20-%20Abnormal%20Port%20to%20Protocol.yaml)
- [GSA - Detect Source IP Scanning Multiple Open Ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Analytic%20Rules/SWG%20-%20Source%20IP%20Port%20Scan.yaml)

### Workbooks (2)

**In solution [Global Secure Access](../solutions/global-secure-access.md):**
- [GSAM365EnrichedEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Workbooks/GSAM365EnrichedEvents.json)
- [GSANetworkTraffic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Workbooks/GSANetworkTraffic.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
