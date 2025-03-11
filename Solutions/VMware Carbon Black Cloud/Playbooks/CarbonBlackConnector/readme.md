# CarbonBlack Logic Apps Custom connector

![](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/VMware%20Carbon%20Black%20Cloud/Playbooks/CarbonBlackConnector/CarbonBlack.PNG)

This custom connector connects to CarbonBlack cloud end point and performs different actions on alerts, devices and threats using CarbonBlack cloud endpoint API.

### Authentication methods this connector supports

*  API Key authentication

### Prerequisites in Carbon Black
1. CarbonBlack cloud end point should be known. (e.g.  https://{CarbonblackBaseURL})
2. Generate an API key. [Refer this link on how to generate the API Key](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key) with the relevant Access level:

| **Actions in the connector** | **API** | **Service Category** | **API Key Access Level(s) Permitted** |
| --------- | -------------- | ----------------- | ------------------------------------ |
| Get endpoints info, Quarantine device, Update policy for a device, Dismiss an alert, Add a note to an alert | Alerts API, Devices API | /appservices/ | Custom (must add an access level with appropriate permissions) |
| Search processes actions | Platform Search API for Processes | /investigate/ | Custom (must add an access level with appropriate permissions) |

## Actions supported by CarbonBlack custom connector

| **Component** | **Description** |
| --------- | -------------- |
| **Get endpoints info** | Get the latest information about an endpoint, including the OS, sensor version and last check-in |
| **Quarantine device** | When the endpoint is suspected to be compromised, isolate it so that the only network communication allowed is with Carbon Black Cloud |
| **Update policy for a device** | Move the endpoint to a more restrictive policy |
| **Search for processes by query** | Find all devices where a certain process (by name of hash) has executed |
| **Search for a process metadata by process GUID** | Get all metadata (such as hash, duration, cmdline) of a specific process following a watchlist hit |
| **Search for processes events by process GUID and (optional) event query** | Get relevant events of a watchlist hint |
| **Dismiss an alert** |Dismiss the alert in Carbon Black Cloud with comments. If an analyst looks in the CBC console, they will not longer see that alert and mistakenly triage it|
| **Add a note to an alert** | Add a comment to provide context, in the case someone looks in the CBC console |
### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required parameters:
    * Custom Connector Name: Enter the Custom connector name (e.g. CarbonBlackCloudConnector)
    * Service Endpoint: Enter the CarbonBlack cloud end point (e.g. https://{CarbonblackBaseURL})

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVMware%2520Carbon%2520Black%2520Cloud%2FPlaybooks%2FCarbonBlackConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVMware%2520Carbon%2520Black%2520Cloud%2FPlaybooks%2FCarbonBlackConnector%2Fazuredeploy.json)