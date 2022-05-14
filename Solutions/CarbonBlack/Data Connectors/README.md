# VMware Carbon Black Logic App custom connector

<img src="./CarbonBlack.PNG" alt="drawing" width="20%"/><br>

> **Important**
>
> The playbooks, workbook, and analytic rules included in `\Solutions\CarbonBlack` should be deployed from the [Microsoft Sentinel content hub]('https://docs.microsoft.com/azure/sentinel/sentinel-solutions-deploy#install-or-update-a-solution') rather than being deployed using the documentation below.
>
> This solution requires the [VMware Carbon Black Endpoint Standard Sentinel data connector]('https://docs.microsoft.com/azure/sentinel/data-connectors-reference#vmware-carbon-black-endpoint-standard-preview') from the Data Connector gallery.
>

This Logic App custom connector connects to Carbon Black cloud end point and performs different actions on alerts, devices and threats using CarbonBlack cloud endpoint API.

## Authentication methods

API key authentication is the only supported authentication method. 

## Carbon Black Cloud connector prerequisites

1. The Carbon Black custom connector must be already be deployed in same subscription as this playbook.
2. Know your Carbon Black Cloud API service endpoint. [Determine your Carbon Black Cloud API service endpoint.](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#building-your-base-urls) (e.g. https://defense.conferdeploy.net)
3. Know your Carbon Black Org Key [Where is the Carbon Black Org Key found?](https://community.carbonblack.com/t5/Knowledge-Base/Carbon-Black-Cloud-Where-is-the-Org-Key-Found/ta-p/80970)
4. Create a custom Access level with the following minimum access:

   * Device > General Information > “device” allow permissions for “READ”
   * Device > Policy assignment > “device.policy” allow permissions for “UPDATE”
   * Device > Quarantine > “device.quarantine” allow permissions for “EXECUTE”
   * Search > Events > “org.search.events”, allow permission to CREATE to start a job, READ to get results, DELETE to cancel a search and UPDATE for watchlist actions.
   * Alerts > General Information > “org.alerts” allow permissions for “READ”
   * Alerts > Dismiss > “org.alerts.dismiss” allow permissions for “EXECUTE”
   * Alerts > Notes > “org.alerts.notes” allow permissions for “CREATE”, “READ”, and “DELETE”
  
5. Create an API key and API Secret using the Access Level type "Custom", and the Access Level you created. [How to generate a Carbon Black Cloud API Key](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)


| **Connector actions** | **API** | **Service Category** | **API Key Access Level(s) Permitted** |
| --------- | -------------- | ----------------- | ------------------------------------ |
| Get endpoints info, Quarantine device, Update policy for a device, Dismiss an alert, Add a note to an alert | Alerts API, Devices API | `/appservices/` | Custom (must add an access level with appropriate permissions) |
| Search processes actions | Platform Search API for Processes | `/investigate/` | Custom (must add an access level with appropriate permissions) |

## Actions supported by Carbon Black custom connector

| **Component** | **Description** |
| --------- | -------------- |
| **Get endpoints info** | Get the latest information about an endpoint, including the OS, sensor version and last check-in |
| **Quarantine device** | When the endpoint is suspected to be compromised, isolate it so that the only network communication allowed is with Carbon Black Cloud |
| **Update policy for a device** | Move the endpoint to a more restrictive policy |
| **Search for processes by query** | Find all devices where a certain process (by name of hash) has executed |
| **Search for a process metadata by process GUID** | Get all metadata (such as hash, duration, command line) of a specific process following a watchlist hit |
| **Search for processes events by process GUID and (optional) event query** | Get relevant events of a watchlist hint |
| **Dismiss an alert** |Dismiss the alert in Carbon Black Cloud with comments. If an analyst looks in the CBC console, they will not longer see that alert and mistakenly triage it|
| **Add a note to an alert** | Add a comment to provide context, in the case someone looks in the CBC console |

## Deployment instructions

1. Deploy the custom connector by clicking on "Deploy to Azure" button. This will take you to the Deploy an ARM Template wizard.
2. Fill in the required parameters:
  
  * Custom connector Name: Enter the custom connector name (e.g. CarbonBlackCloudConnector)
  * Service Endpoint: Enter the Carbon Black Cloud API service endpoint (e.g. https://dashboard.confer.net )

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2FData%20Connectors%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2FData%20Connectors%2Fazuredeploy.json)
