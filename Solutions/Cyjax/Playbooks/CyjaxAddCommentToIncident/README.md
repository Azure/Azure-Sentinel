# Cyjax Add Comment To Incident

## Summary

This playbook is triggered via HTTP request and is designed to be used as a sub-playbook by other Cyjax playbooks (such as CyjaxIncidentEnrichment). It receives enrichment data for various entity types (host, domain, hash, URL, Email) along with the incident ARM ID and parent playbook name. The playbook processes each data type, extracts relevant fields, formats them into HTML tables, and adds them as comments to the Microsoft Sentinel incident.

### Prerequisites

1. This playbook is intended to be called as a sub-playbook by other Cyjax playbooks.
2. Ensure the parent playbook (CyjaxIncidentEnrichment, etc.) is deployed and configured.
3. Ensure you have appropriate permissions to add comments to Microsoft Sentinel incidents.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: CyjaxAddCommentToIncident).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCyjax%2FPlaybooks%2FCyjaxAddCommentToIncident%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCyjax%2FPlaybooks%2FCyjaxAddCommentToIncident%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize the Microsoft Sentinel connection.
1. Go to your logic app → API connections → Select Microsoft Sentinel connection resource.
2. Go to General → edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.

#### b. Configure Parent Playbooks

Configure the parent playbooks (CyjaxIncidentEnrichment, etc.) to call this sub-playbook using its HTTP trigger URL.
1. Go to Logic App → *your Logic App* → Logic app designer.
2. Copy the HTTP POST URL from the trigger.
3. Update the parent playbook configuration to use this URL when adding incident comments.

#### c. Verify Permissions

Ensure the playbook has appropriate permissions to add comments to incidents.
1. Verify the managed identity has Microsoft Sentinel Responder role or equivalent permissions.
2. Test the playbook by triggering it from a parent playbook with sample enrichment data.
