# Cisco Secure Endpoint

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-28 |
| **Last Updated** | 2022-02-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[DEPRECATED] Cisco Secure Endpoint (AMP)](../connectors/ciscosecureendpoint.md)
- [Cisco Secure Endpoint (via Codeless Connector Framework)](../connectors/ciscosecureendpointlogsccpdefinition.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md) | [Cisco Secure Endpoint (via Codeless Connector Framework)](../connectors/ciscosecureendpointlogsccpdefinition.md) | Analytics, Hunting, Workbooks |
| [`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md) | [Cisco Secure Endpoint (via Codeless Connector Framework)](../connectors/ciscosecureendpointlogsccpdefinition.md) | Analytics, Hunting, Workbooks |
| [`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) | [[DEPRECATED] Cisco Secure Endpoint (AMP)](../connectors/ciscosecureendpoint.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **23 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 11 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Cisco SE - Connection to known C2 server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Analytic%20Rules/CiscoSEC2Connection.yaml) | High | CommandAndControl | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Dropper activity on host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Analytic%20Rules/CiscoSEDropperActivity.yaml) | High | Execution | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Generic IOC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Analytic%20Rules/CiscoSEGenIoC.yaml) | High | Execution | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Malware execusion on host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Analytic%20Rules/CiscoSEMalwareExecution.yaml) | High | Execution | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Malware outbreak](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Analytic%20Rules/CiscoSEMalwareOutbreak.yaml) | High | InitialAccess | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Multiple malware on host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Analytic%20Rules/CiscoSEMultipleMalwareOnHost.yaml) | High | InitialAccess | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Policy update failure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Analytic%20Rules/CiscoSEPolicyUpdateFailure.yaml) | Medium | DefenseEvasion | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Possible webshell](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Analytic%20Rules/CiscoSEWebshell.yaml) | High | CommandAndControl | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Ransomware Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Analytic%20Rules/CiscoSERansomwareActivityOnHost%20copy.yaml) | High | Impact | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Unexpected binary file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Analytic%20Rules/CiscoSEUnexpectedBinary.yaml) | Medium | InitialAccess | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE High Events Last Hour](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Analytic%20Rules/CiscoEndpointHighAlert.yaml) | High | Execution, InitialAccess | [`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Cisco SE - Infected hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Hunting%20Queries/CiscoSEInfectedHosts.yaml) | Execution | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Infected users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Hunting%20Queries/CiscoSEInfectedUsers.yaml) | Execution | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Malicious files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Hunting%20Queries/CiscoSEMaliciousFiles.yaml) | Execution | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Modified agents on hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Hunting%20Queries/CiscoSEModifiedAgent.yaml) | DefenseEvasion | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Rare scanned files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Hunting%20Queries/CiscoSERareFilesScanned.yaml) | Execution | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Scanned files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Hunting%20Queries/CiscoSEScannedFiles.yaml) | Execution | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Suspicious powershel downloads](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Hunting%20Queries/CiscoSESuspiciousPSDownloads.yaml) | Execution | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Uncommon application behavior](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Hunting%20Queries/CiscoSEUncommonApplicationBehavior.yaml) | Execution | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - User Logins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Hunting%20Queries/CiscoSELoginsToConsole.yaml) | InitialAccess | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |
| [Cisco SE - Vulnerable applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Hunting%20Queries/CiscoSEVulnerableApplications.yaml) | Execution | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Cisco Secure Endpoint Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Workbooks/Cisco%20Secure%20Endpoint%20Overview.json) | [`CiscoSecureEndpointAuditLogsV2_CL`](../tables/ciscosecureendpointauditlogsv2-cl.md)<br>[`CiscoSecureEndpointEventsV2_CL`](../tables/ciscosecureendpointeventsv2-cl.md)<br>[`CiscoSecureEndpoint_CL`](../tables/ciscosecureendpoint-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CiscoSecureEndpoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Parsers/CiscoSecureEndpoint.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                             |
|-------------|-------------------------------|-----------------------------------------------|
| 3.0.2       | 14-08-2025                    | Cisco Secure Endpoint **CCF Connector** moving to GA. |
| 3.0.1       | 23-06-2025                    | Adding a new **CCF Data Connector** - *Cisco Secure Endpoint*  and updated the **Parser** to handle the newly introduced table.  	   |
| 3.0.0       | 28-08-2024                    | Updated the python runtime version to 3.11.    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
