# Carbon Black Logic Apps custom connector

<img src="./CarbonBlack.PNG" alt="drawing" width="20%"/><br>

This custom connector connects to Carbon Black cloud end point and performs different actions on alerts, devices and threats using CarbonBlack cloud endpoint API.

## Supported authentication methods

* API Key authentication

## Carbon Black Prerequisites

1. You need to know the Carbon Black Cloud endpoint URL. (e.g.  https://{CarbonblackBaseURL})
2. Generate an API key. [Refer this link on how to generate the API Key](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key) with the required access level.

| **Connector actions** | **API** | **Service Category** | **API Key Access Level(s) Permitted** |
| --------- | -------------- | ----------------- | ------------------------------------ |
| Get endpoints info, Quarantine device, Update policy for a device, Dismiss an alert, Add a note to an alert | Alerts API, Devices API | /appservices/ | Custom (must add an access level with appropriate permissions) |
| Search processes actions | Platform Search API for Processes | /investigate/ | Custom (must add an access level with appropriate permissions) |

## Actions supported by Carbon Black custom connector

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

## Deployment instructions

1. Deploy the custom connector by clicking on "Deploy to Azure" button. This will take you to the Deploy an ARM Template wizard.
2. Fill in the required parameters:

  * Custom connector Name: Enter the Custom connector name (e.g. CarbonBlackCloudConnector)
  * Service Endpoint: Enter the Carbon Black Cloud API endpoint (e.g. https://{CarbonblackBaseURL})

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2FData%20Connectors%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2FData%20Connectors%2Fazuredeploy.json)

