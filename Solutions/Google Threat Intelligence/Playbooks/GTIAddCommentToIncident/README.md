# Google Threat Intelligence Add Comment To Incident

## Summary

This playbook is triggered via HTTP request and is designed to be used as a sub-playbook by other GTI playbooks, such as GTIURLScanIncidentEnrichment and GTIURLScanEntityEnrichment. It receives the incident ARM ID, the raw GTI URL scan response object, the scanned URL, and the calling playbook's name. It fetches the current incident comment count, formats the scan results (verdict, severity, threat score, contributing factors, URL details, and context) into an HTML table, enforces a 99-comment and 30,000-character-per-comment limit, and posts the resulting comment to the Microsoft Sentinel incident.

### Prerequisites

1. This playbook is intended to be called as a sub-playbook by other GTI playbooks.
2. Ensure the parent playbook(s) (GTIURLScanIncidentEnrichment, GTIURLScanEntityEnrichment, etc.) are deployed and configured.
3. Ensure you have appropriate permissions to add comments to Microsoft Sentinel incidents.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: GTIAddCommentToIncident).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIAddCommentToIncident%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIAddCommentToIncident%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize the Microsoft Sentinel connection.
1. Go to your logic app → API connections → Select Microsoft Sentinel connection resource.
2. Go to General → edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.

#### b. Configure Parent Playbooks

Configure the parent GTI playbooks (GTIURLScanIncidentEnrichment, GTIURLScanEntityEnrichment, etc.) to call this sub-playbook using its HTTP trigger URL.
1. Go to Logic App → *your Logic App* → Logic app designer.
2. Copy the HTTP POST URL from the trigger.
3. Update each parent playbook's "Call comment sub-playbook" action to pass `incidentArmId`, `scanResponse`, `urlScanned`, and `playbookName` to this URL.

#### c. Verify Permissions

Ensure the playbook has appropriate permissions to add comments to incidents.
1. Verify the managed identity has Microsoft Sentinel Responder role or equivalent permissions.
2. Test the playbook by triggering it from a parent playbook with sample enrichment data.
