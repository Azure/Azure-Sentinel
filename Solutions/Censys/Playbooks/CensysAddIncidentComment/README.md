# Censys Add Incident Comment

## Summary

This playbook is triggered via HTTP request and is designed to be used as a sub-playbook by other Censys playbooks (CensysIncidentEnrichment, CensysEntityEnrichmentHost, CensysEntityEnrichmentCertificate, CensysEntityEnrichmentWebProperty, CensysAlertEnrichment). It receives enrichment data (host, web_property, certificate) along with the incident ARM ID and parent playbook name. The playbook processes each data type, extracts relevant fields (IP, autonomous system, WHOIS, location, DNS, services, threats, vulnerabilities, labels, software), formats them into HTML tables, and adds them as comments to the Microsoft Sentinel incident. It handles comment character limits (splitting into multiple comments if needed) and enforces a maximum of 100 comments per incident. The enrichment data is also ingested into Azure Log Analytics custom tables (Incident_Enrich_Host_Data_CL, Incident_Enrich_WebProperty_Data_CL, Incident_Enrich_Certificate_Data_CL) for historical analysis. The playbook includes comprehensive error handling and returns appropriate HTTP responses.

### Prerequisites

1. This playbook is intended to be called as a sub-playbook by other Censys playbooks.
2. Ensure the parent playbook (CensysEnrichment, CensysEntityEnrichmentHost, etc.) is deployed and configured.
3. The Log Analytics workspace must be configured to receive custom logs.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: CensysAddIncidentComment).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCensys%2FPlaybooks%2FCensysAddIncidentComment%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCensys%2FPlaybooks%2FCensysAddIncidentComment%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select Microsoft Sentinel connection resource.
2. Go to General → Edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for Log Analytics Data Collector connection.

#### b. Configure parent playbooks

Configure the parent playbooks to call this sub-playbook using its HTTP trigger URL.
1. Go to Logic App → *your Logic App* → Logic app designer.
2. Copy the HTTP POST URL from the trigger.
3. Use this URL in parent playbooks (CensysEnrichment, CensysEntityEnrichmentHost, etc.) to invoke this sub-playbook.

#### c. Permissions

Ensure the playbook has appropriate permissions to add comments to incidents.
1. Go to Log Analytics workspace → Access control (IAM) → Add role assignment.
2. Select Microsoft Sentinel Contributor role.
3. Select Managed identity and choose the playbook's identity.
4. Click Save.
