# Threat intelligence - TAXII

| | |
|----------|-------|
| **Connector ID** | `ThreatIntelligenceTaxii` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ThreatIntelIndicators`](../tables-index.md#threatintelindicators), [`ThreatIntelObjects`](../tables-index.md#threatintelobjects), [`ThreatIntelligenceIndicator`](../tables-index.md#threatintelligenceindicator) |
| **Used in Solutions** | [Threat Intelligence](../solutions/threat-intelligence.md), [Threat Intelligence (NEW)](../solutions/threat-intelligence-(new).md) |
| **Connector Definition Files** | [template_ThreatIntelligenceTaxii.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Data%20Connectors/template_ThreatIntelligenceTaxii.json) |

Microsoft Sentinel integrates with TAXII 2.0 and 2.1 data sources to enable monitoring, alerting, and hunting using your threat intelligence. Use this connector to send the supported STIX object types from TAXII servers to Microsoft Sentinel. Threat indicators can include IP addresses, domains, URLs, and file hashes. For more information, see the [Microsoft Sentinel documentation >](https://go.microsoft.com/fwlink/p/?linkid=2224105&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **TAXII Server**: TAXII 2.0 or TAXII 2.1 Server URI and Collection ID.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure TAXII servers to stream STIX 2.0 or 2.1 STIX objects to Microsoft Sentinel**

You can connect your TAXII servers to Microsoft Sentinel using the built-in TAXII connector. For detailed configuration instructions, see the [full documentation](https://docs.microsoft.com/azure/sentinel/import-threat-intelligence#adding-threat-indicators-to-azure-sentinel-with-the-threat-intelligence---taxii-data-connector). 

Enter the following information and select Add to configure your TAXII server.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `ThreatIntelligenceTaxii`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
