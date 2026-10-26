# Google Threat Intelligence - Threat List

## Summary

This playbook runs automatically on a Recurrence schedule (every 60 minutes) and calls the Google Threat Intelligence Threat List API for the `ransomware` category to retrieve the current STIX indicators for that period. The returned indicators are chunked into batches of 100 and uploaded to Microsoft Sentinel Threat Intelligence via the Upload STIX Objects action, so no manual trigger or workbook wiring is required.

### Prerequisites

1. Register for Google Threat Intelligence and obtain an API key (see https://developers.virustotal.com/v3.0/reference#getting-started).
2. Deploy the Google Threat Intelligence Custom Connector (`GTICustomConnector`) in the same resource group, and configure its API connection with the GTI API key.
3. Ensure you have a Log Analytics Workspace onboarded to Microsoft Sentinel to receive the ingested Threat Intelligence indicators.
4. Grant the playbook's managed identity the **Microsoft Sentinel Contributor** (or **Threat Intelligence Contributor**) role so it can upload STIX objects via the Microsoft Sentinel connector.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: GTI-ThreatList).
   * ConnectorName: Name of the previously deployed Google Threat Intelligence custom connector resource (default: GoogleThreatIntelligence-CustomConnector).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIThreatList%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIThreatList%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select the GoogleThreatIntelligence-CustomConnector connection resource.
2. Go to General → edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for the GoogleThreatIntelligence-MicrosoftSentinelConnection connection.

#### b. Verify Scheduled Run

This playbook runs automatically on the configured Recurrence interval once enabled — no manual trigger wiring is required.
1. Go to Logic App → *your Logic App* → Overview, and confirm the trigger history shows successful runs after the first interval elapses.
2. Adjust the recurrence interval or redeploy with an updated ConnectorName if needed.
3. Confirm ingested indicators appear under Microsoft Sentinel → Threat Intelligence.
