# Google Threat Intelligence - IoC Stream

## Summary

This playbook runs automatically on a Recurrence trigger (every 60 minutes) and does not require manual invocation from the workbook. On each run it queries the Google Threat Intelligence `/ioc_stream` API (filtered by the timestamp of the last successful run, `output_format=stix`) and pages through results using the returned `cursor` until the API stops returning one. Each page of STIX objects is uploaded into Microsoft Sentinel Threat Intelligence via the "Upload STIX Objects" action, so the indicators from your GTI IoC Stream become available as threat intelligence indicators in Sentinel. An Azure Table is used to persist the last-execution timestamp between runs so each recurrence only pulls new IoCs.

### Prerequisites

1. Deploy the Google Threat Intelligence custom connector (`GTICustomConnector`) first — it authenticates to the GTI API using an API key sent in the `x-apikey` header.
2. Obtain a Google Threat Intelligence API key; you will enter it when authorizing the custom connector after deployment.
3. Ensure you have a Log Analytics Workspace configured for Microsoft Sentinel, and an Azure Storage Account available for the Azure Tables connection (used to track the last execution timestamp/cursor).

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: GTI-IoCStream).
   * ConnectorName: Name of the Google Threat Intelligence custom connector resource to bind to (default: GoogleThreatIntelligence-CustomConnector).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIIocStream%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIIocStream%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select GoogleThreatIntelligence-CustomConnector connection resource.
2. Go to General → edit API connection.
3. Click Authorize, enter your GTI API key when prompted.
4. Click Save.
5. Repeat steps for the GoogleThreatIntelligence-MicrosoftSentinelConnection (Microsoft Sentinel) and GoogleThreatIntelligence-AzureTablesConnection (Azure Tables) connections, signing in with an account authorized for the respective resources.

#### b. Confirm the Recurrence schedule

This playbook is Recurrence-triggered (default: every 60 minutes) and requires no additional wiring to the Google Threat Intelligence workbook.
1. Go to Logic App → *your Logic App* → Logic app designer.
2. Open the Recurrence trigger and confirm/adjust the interval, frequency, and time zone to suit your ingestion cadence.
3. Save the workflow; it will begin running automatically on the configured schedule, pulling new IoC Stream data into Microsoft Sentinel Threat Intelligence on every run.
