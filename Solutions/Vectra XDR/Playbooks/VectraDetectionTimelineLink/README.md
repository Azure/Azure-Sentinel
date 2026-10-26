# Vectra Detection Timeline Link

## Summary

This playbook will trigger when a Vectra RUX incident is created. It queries the Detections data to resolve the Detection ID and Vectra URL for the incident's detection and entity, then posts a comment to the incident containing a Vectra pivot link and a link to the Vectra Detection Timeline workbook for quick investigation.

### Prerequisites

1. The Vectra XDR data connector should be configured to create alerts and generate an incident based on entity data in Microsoft Sentinel.
2. The Vectra Detection Timeline workbook should be deployed. Obtain its full ARM resource ID to provide as the WorkbookResourceId parameter. Example: /subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Insights/workbooks/{guid}
3. Obtain the Log Analytics workspace name and workspace GUID (customerId) in which the Vectra XDR data connector is deployed. The workspace GUID can be retrieved with: az monitor log-analytics workspace show --resource-group <rg> --workspace-name <workspace> --query customerId -o tsv

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here.
   * WorkspaceName: Enter name of the log analytics workspace where incidents are available using generated using analytic rule.
   * WorkbookResourceId: Enter the full ARM resource ID of the deployed Vectra Detection Timeline workbook.
   * WorkspaceId: Enter the Log Analytics workspace GUID (customerId).
   * azure log analytics: Log Analytics query API domain (appended to the hardcoded `https://api.` prefix). Defaults to `loganalytics.io` (Azure public cloud); change this if deploying to a sovereign/national cloud (e.g. `loganalytics.us` for Azure Government).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraDetectionTimelineLink%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraDetectionTimelineLink%2Fazuredeploy.json)

## Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select azuresentinel connection resource.
2. Go to General → Edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for other connections.

#### b. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, configure an automation rule to trigger the playbook on incident creation.
   -  Go to Microsoft Sentinel → *your workspace* → Automation
   -  Click on Create → Automation rule
   -  Provide a name for your rule
   -  In the trigger, select 'When incident is created'
   -  In the condition, filter by Analytic rule name containing 'Vectra RUX'
   -  In Actions dropdown select Run playbook
   -  In second dropdown select this deployed playbook
   -  Click on Apply
   -  Save the Automation rule.
**NOTE**: If you want to manually run the playbook on a particular incident follow the below steps:
   -  Go to Microsoft Sentinel → *your workspace* → Incidents
   -  Select an incident.
   -  In the right pane, click on Actions, and from the dropdown select the 'Run Playbook' option.
   -  Click on the Run button beside this playbook.
