# PaloAlto-PAN-OS-GetThreatPCAP

 ## Summary

This playbook allows us to get a threat PCAP for a given PCAP ID. 

When a new Sentinel incident is created, this playbook gets triggered and performs below actions:

1. Gets the various parameters from the alert

2. Gets the PCAP from the device.

3. Puts the PCAP in Blob Storage

4. Creates a Sentinel Incident and updates it with a link to the blob.



### Prerequisites 
1. PaloAlto connector needs to be deployed prior to the deployment of this playbook under the same subscription. Relevant instructions can be found in the connector doc page.
2. Generate an API key.[Refer this link on how to generate the API Key](https://docs.paloaltonetworks.com/pan-os/10-1/pan-os-panorama-api/get-started-with-the-pan-os-xml-api/get-your-api-key)
3. This playbook only works for Palo Alto incidents with a threat PCAP where the PCAP ID is not null or zero. 


### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.



[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FPaloAlto-PAN-OS%2FPlaybooks%2FPaloAltoPlaybooks%2FPaloAlto-PAN-OS-GetThreatPCAP%2Fazuredeploy.json)   [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FPaloAlto-PAN-OS%2FPlaybooks%2FPaloAltoPlaybooks%2FPaloAlto-PAN-OS-GetThreatPCAP%2Fazuredeploy.json)


2. Fill in the required parameters:
    * Playbook Name: The playbook name here (e.g. PaloAlto-PAN-OS-GetThreatPCAP)
    * StorageAccountName:  The blob storage account where the threat PCAP will be stored
    * StorageAccountFolderPath: The folder in the blob storage account where the threat PCAP will be stored
    * LogAnalyticsResourceGroup: The Log Analytics resource group for logging for the Playbook.
    * LogAnalyticsResourceName: The Log Analytics resource for logging for the Playbook.
	* CustomConnectorName : Name of the custom connector, if you want to change the default name, make sure to use the same in all PaloAlto automation playbooks as well

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Microsoft Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connections such as Blob Store connection and PAN-OS API connection (For authorizing the PAN-OS API connection, API Key needs to be provided)

#### b. Configurations in Sentinel
1. In Microsoft sentinel analytical rules should be configured to trigger an incident with results having column "TimeGenerated", "Computer", "pcap_id", "sessionid", "event_time".
2. Entity mapping not needed beacuse playbook will internally hit the query again and fetches the required column from result. 
3. Configure the automation rules to trigger this playbook

#### c. Assign Playbook Microsoft Sentinel Responder Role
1. Select the Playbook (Logic App) resource
2. Click on Identity Blade
3. Choose System assigned tab
4. Click on Azure role assignments
5. Click on Add role assignments
6. Select Scope - Resource group
7. Select Subscription - where Playbook has been created
8. Select Resource group - where Playbook has been created
9. Select Role - Microsoft Sentinel Responder
10. Click Save (It takes 3-5 minutes to show the added role.)

## Playbook steps explained

### When Microsoft Sentinel incident creation rule is triggered

Microsoft Sentinel incident is created. The playbook receives the incident as the input.

### Run Query and List Results

Get the logs from the incident.

### For Each 

Iterates on each result and performs the following:

#### If alert is Palo Alto alert
Checks if the alert is a Palo Alto alert. Required when logs from various devices are present

##### If PCAP ID exists
Checks if a PCAP ID is present, and that it is not equal to zero. If the PCAP ID is absent or if it is zero, no PCAP exists.

###### Query XML API
Sets the PCAP ID, time generated, Session ID and the device name, and queries the device's XML API to retrieve a threat PCAP


###### Create Blob (V2)
Creates a blob in aV2 blob storage account, denoted by Storage Account Name, in the folder denoted by the Folder Path with a name of the type "paloalto1235678920220101102000.pcap" where the name is a concatenation of the  "paloalto"+pcapid+timegenerated+".pcap"

###### Alert - Get Incident
Creates Incident for the alert

###### Add Comment to Incident (V3)
Adds a comment containing a link to the pcap in the blob storage to the incident 

 
