# Threat intelligence - TAXII Export (Preview)

| | |
|----------|-------|
| **Connector ID** | `ThreatIntelligenceTaxiiExport` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ThreatIntelExportOperation`](../tables-index.md#threatintelexportoperation) |
| **Used in Solutions** | [Threat Intelligence (NEW)](../solutions/threat-intelligence-(new).md) |
| **Connector Definition Files** | [template_ThreatIntelligenceTaxiiExport.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Data%20Connectors/template_ThreatIntelligenceTaxiiExport.json) |

Microsoft Sentinel integrates with TAXII 2.1 servers to enable exporting of your threat intelligence objects. Use this connector to send the supported STIX object types from Microsoft Sentinel to TAXII servers.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **TAXII Server**: TAXII 2.1 Server URL and Collection ID.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure TAXII servers to export STIX 2.1 objects to. Once configured, you can start exporting STIX objects from your TI repository**
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `ThreatIntelligenceTaxii`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
