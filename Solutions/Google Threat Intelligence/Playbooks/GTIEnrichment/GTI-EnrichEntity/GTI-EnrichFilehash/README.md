# Google Threat Intelligence - FileHash Enrichment

## Summary

This playbook is triggered manually from a FileHash entity in a Microsoft Sentinel incident. It calls the Google Threat Intelligence API to retrieve the file report for the selected hash, including its reputation, last-analysis statistics (harmless/malicious/suspicious/timeout/undetected), community votes, and GTI Assessment (threat score, verdict, severity). If the entity is associated with an incident, the playbook formats these details and adds them as a comment on the incident, giving the analyst enriched file context without leaving Microsoft Sentinel.

### Prerequisites

1. Deploy the Google Threat Intelligence Custom Connector (GTICustomConnector) before deploying this playbook, and note its resource name for the ConnectorName parameter.
2. Register for a Google Threat Intelligence account and obtain an API key, then configure it on the Google Threat Intelligence Custom Connector's API connection.
3. Ensure you have a Log Analytics Workspace configured for Microsoft Sentinel.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: GTI-IOCEnrichmentFileHash).
   * ConnectorName: Name of the deployed Google Threat Intelligence Custom Connector resource (default: GoogleThreatIntelligence-CustomConnector).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIEnrichment%2FGTI-EnrichEntity%2FGTI-EnrichFilehash%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIEnrichment%2FGTI-EnrichEntity%2FGTI-EnrichFilehash%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select Microsoft Sentinel connection resource.
2. Go to General → edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for the Google Threat Intelligence Custom Connector connection.

#### b. Attach to FileHash Entity

This is an entity-triggered playbook that runs against a FileHash entity.
1. Go to Microsoft Sentinel → Incidents, open an incident, and select the Entities tab.
2. Right-click the FileHash entity you want to enrich.
3. Select Run playbook.
4. Choose GTI-IOCEnrichmentFileHash (or the PlaybookName you deployed) and run it.
5. If the entity is linked to an incident, the enriched GTI File Report is added as a comment on that incident.
