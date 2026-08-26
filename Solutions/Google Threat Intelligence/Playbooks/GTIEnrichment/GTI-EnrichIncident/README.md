# Google Threat Intelligence - IOC Enrichment (Incident)

## Summary

This playbook triggers automatically when a Microsoft Sentinel incident is created. It retrieves the IP address, file hash, URL, and DNS resolution (domain) entities related to the incident, then queries the Google Threat Intelligence (GTI) API for each entity to pull its reputation, threat score, severity, and verdict. The results are formatted into HTML summaries and posted back onto the incident as comments, giving analysts GTI threat context for every IOC without leaving Sentinel.

### Prerequisites

1. Deploy the GTICustomConnector custom connector before deploying this playbook.
2. Register for a Google Threat Intelligence account to obtain an API key, and configure it on the GTICustomConnector API connection.
3. Ensure you have a Log Analytics Workspace configured for Microsoft Sentinel.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: GTI-IOCEnrichmentIncident).
   * ConnectorName: Name of the deployed Google Threat Intelligence custom connector (API connection) used for the enrichment lookups (default: GoogleThreatIntelligence-CustomConnector).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIEnrichment%2FGTI-EnrichIncident%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIEnrichment%2FGTI-EnrichIncident%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select Microsoft Sentinel connection resource.
2. Go to General → edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for the Google Threat Intelligence connection.

#### b. Attach to Automation Rule or Manual Trigger

This playbook fires on the Microsoft Sentinel incident-creation trigger, so it can run automatically or be invoked manually:
1. **For Automatic Enrichment**: Create an automation rule in Microsoft Sentinel that runs when an incident is created, and add this playbook (GTI-IOCEnrichmentIncident) as its action.
2. **For Manual Enrichment**: Open the incident in Microsoft Sentinel, select "Run playbook", and choose GTI-IOCEnrichmentIncident from the list.
3. Once triggered, the playbook iterates over all entities associated with the incident, adding enrichment comments to the incident.
