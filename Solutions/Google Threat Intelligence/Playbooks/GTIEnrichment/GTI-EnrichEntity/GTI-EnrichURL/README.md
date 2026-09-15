# Google Threat Intelligence - URL Enrichment

## Summary

This playbook is triggered by the Microsoft Sentinel entity trigger for a URL entity. When run, it calls the Google Threat Intelligence API to retrieve the URL report (reputation, harmless/malicious/suspicious/timeout/undetected detection counts, community votes, and the GTI Assessment threat score, verdict, and severity). If the trigger context includes an associated incident, the playbook formats these results into HTML and adds them as a comment on that incident, giving the analyst an at-a-glance threat assessment of the URL directly in the incident timeline.

### Prerequisites

1. Deploy the GTICustomConnector custom connector before deploying this playbook, and register for a Google Threat Intelligence API key (https://developers.virustotal.com/v3.0/reference#getting-started) to use when authorizing the connector's API connection.
2. Ensure you have a Log Analytics Workspace configured for Microsoft Sentinel.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: GTI-IOCEnrichmentURL).
   * ConnectorName: Name of the deployed Google Threat Intelligence custom connector (default: GoogleThreatIntelligence-CustomConnector).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIEnrichment%2FGTI-EnrichEntity%2FGTI-EnrichURL%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIEnrichment%2FGTI-EnrichEntity%2FGTI-EnrichURL%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select Microsoft Sentinel connection resource.
2. Go to General → edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for the Google Threat Intelligence connection, providing your GTI API key when prompted.

#### b. Attach to URL Entity

This playbook uses the Microsoft Sentinel entity trigger (path `UrlEntity`) and is intended to be run against a URL entity on an incident:
1. Open an incident in Microsoft Sentinel that contains a URL entity.
2. Select the URL entity, then choose **Run playbook**.
3. From the list of playbooks, select this playbook (default name: GTI-IOCEnrichmentURL).
4. The playbook retrieves the GTI URL report and, when the run is associated with an incident, adds the GTI URL Report (reputation, detection stats, votes, and GTI Assessment) as a comment on that incident.
