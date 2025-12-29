# Netskopev2

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Netskope |
| **Support Tier** | Partner |
| **Support Link** | [https://www.netskope.com/services#support](https://www.netskope.com/services#support) |
| **Categories** | domains |
| **First Published** | 2024-03-18 |
| **Last Updated** | 2024-03-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [Netskope Alerts and Events](../connectors/netskopealertsevents.md)

**Publisher:** Netskope

### [Netskope Data Connector](../connectors/netskopedataconnector.md)

**Publisher:** Netskope

### [Netskope Web Transactions Data Connector](../connectors/netskopewebtransactionsdataconnector.md)

**Publisher:** Netskope

The [Netskope Web Transactions](https://docs.netskope.com/en/netskope-help/data-security/transaction-events/netskope-transaction-events/) data connector provides the functionality of a docker image to pull the Netskope Web Transactions data from google pubsublite, process the data and ingest the processed data to Log Analytics. As part of this data connector two tables will be formed in Log Analytics, one for Web Transactions data and other for errors encountered during execution.





 For more details related to Web Transactions refer to the below documentation: 

 1. Netskope Web Transactions documentation: 

> https://docs.netskope.com/en/netskope-help/data-security/transaction-events/netskope-transaction-events/ 



**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Azure Subscription**: Azure Subscription with owner role is required to register an application in Microsoft Entra ID and assign role of contributor to app in resource group.
- **Microsoft.Compute permissions**: Read and write permissions to Azure VMs is required. [See the documentation to learn more about Azure VMs](https://learn.microsoft.com/azure/virtual-machines/overview).
- **TransactionEvents Credentials and Permissions**: **Netskope Tenant** and **Netskope API Token** is required. [See the documentation to learn more about Transaction Events.](https://docs.netskope.com/en/netskope-help/data-security/transaction-events/netskope-transaction-events/)
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector provides the functionality of ingesting Netskope Web Transactions data using a docker image to be deployed on a virtual machine (Either Azure VM/On Premise VM). Check the [Azure VM pricing page](https://azure.microsoft.com/pricing/details/virtual-machines/linux) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Steps to create/get Credentials for the Netskope account** 

 Follow the steps in this section to create/get **Netskope Hostname** and **Netskope API Token**:
 1. Login to your **Netskope Tenant** and go to the **Settings menu** on the left navigation bar.
 2. Click on Tools and then **REST API v2**
 3. Now, click on the new token button. Then it will ask for token name, expiration duration and the endpoints that you want to fetch data from.
 5. Once that is done click the save button, the token will be generated. Copy the token and save at a secure place for further usage.

**STEP 2 - Choose one from the following two deployment options to deploy the docker based data connector to ingest Netskope Web Transactions data **

>**IMPORTANT:** Before deploying Netskope data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following) readily available, as well as the Netskope API Authorization Key(s) [Make sure the token has permissions for transaction events].
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Option 1 - Using Azure Resource Manager (ARM) Template to deploy VM [Recommended]**

Using the ARM template deploy an Azure VM, install the prerequisites and start execution.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-NetskopeV2WebTransactions-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the below information : 
		Docker Image Name (mgulledge/netskope-microsoft-sentinel-plugin:netskopewebtransactions)
		Netskope HostName 
		Netskope API Token 
		Seek Timestamp (The epoch timestamp that you want to seek the pubsublite pointer, can be left empty) 
		Workspace ID 
		Workspace Key 
		Backoff Retry Count (The retry count for token related errors before restarting the execution.)  
		Backoff Sleep Time (Number of seconds to sleep before retrying) 
		Idle Timeout (Number of seconds to wait for Web Transactions Data before restarting execution) 
		VM Name 
		Authentication Type 
		Admin Password or Key 
		DNS Label Prefix 
		Ubuntu OS Version 
		Location 
		VM Size 
		Subnet Name 
		Network Security Group Name 
		Security Type 
4. Click on **Review+Create**. 
5. Then after validation click on **Create** to deploy.

**4. Option 2 - Manual Deployment on previously created virtual machine**

Use the following step-by-step instructions to deploy the docker based data connector manually on a previously created virtual machine.

**1. Install docker and pull docker Image**

>**NOTE:** Make sure that the VM is linux based (preferably Ubuntu).

1. Firstly you will need to [SSH into the virtual machine](https://learn.microsoft.com/azure/virtual-machines/linux-vm-connect?tabs=Linux).
2. Now install [docker engine](https://docs.docker.com/engine/install/).
3. Now pull the docker image from docker hub using the command: 'sudo docker pull mgulledge/netskope-microsoft-sentinel-plugin:netskopewebtransactions'.
4. Now to run the docker image use the command: 'sudo docker run -it -v $(pwd)/docker_persistent_volume:/app mgulledge/netskope-microsoft-sentinel-plugin:netskopewebtransactions'. You can replace mgulledge/netskope-microsoft-sentinel-plugin:netskopewebtransactions with the image id. Here docker_persistent_volume is the name of the folder that would be created on the vm in which the files will get stored.

**2. Configure the Parameters**

1. Once the docker image is running it will ask for the required parameters.
2. Add each of the following application settings individually, with their respective values (case-sensitive): 
		Netskope HostName 
		Netskope API Token 
		Seek Timestamp (The epoch timestamp that you want to seek the pubsublite pointer, can be left empty) 
		Workspace ID 
		Workspace Key 
		Backoff Retry Count (The retry count for token related errors before restarting the execution.)  
		Backoff Sleep Time (Number of seconds to sleep before retrying) 
		Idle Timeout (Number of seconds to wait for Web Transactions Data before restarting execution)
3. Now the execution has started but is in interactive mode, so that shell cannot be stopped. To run it as a background process, stop the current execution by pressing Ctrl+C and then use the command: 'sudo docker run -d -v $(pwd)/docker_persistent_volume:/app mgulledge/netskope-microsoft-sentinel-plugin:netskopewebtransactions'.

**3. Stop the docker container**

1. Use the command 'sudo docker container ps' to list the running docker containers. Note down your container id.
2. Now stop the container using the command: 'sudo docker stop *<*container-id*>*'.

| | |
|--------------------------|---|
| **Tables Ingested** | `NetskopeWebtxData_CL` |
| | `NetskopeWebtxErrors_CL` |
| **Connector Definition Files** | [Netskope_WebTransactions.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Data%20Connectors/NetskopeWebTransactionsDataConnector/Netskope_WebTransactions.json) |

[→ View full connector details](../connectors/netskopewebtransactionsdataconnector.md)

## Tables Reference

This solution ingests data into **28 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `NetskopeAlerts_CL` | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) |
| `NetskopeEventsApplication_CL` | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) |
| `NetskopeEventsAudit_CL` | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) |
| `NetskopeEventsConnection_CL` | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) |
| `NetskopeEventsDLP_CL` | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) |
| `NetskopeEventsEndpoint_CL` | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) |
| `NetskopeEventsInfrastructure_CL` | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) |
| `NetskopeEventsNetwork_CL` | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) |
| `NetskopeEventsPage_CL` | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) |
| `NetskopeWebtxData_CL` | [Netskope Web Transactions Data Connector](../connectors/netskopewebtransactionsdataconnector.md) |
| `NetskopeWebtxErrors_CL` | [Netskope Web Transactions Data Connector](../connectors/netskopewebtransactionsdataconnector.md) |
| `Netskope_WebTx_metrics_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `alertscompromisedcredentialdata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `alertsctepdata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `alertsdlpdata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `alertsmalsitedata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `alertsmalwaredata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `alertspolicydata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `alertsquarantinedata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `alertsremediationdata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `alertssecurityassessmentdata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `alertsubadata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `eventsapplicationdata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `eventsauditdata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `eventsconnectiondata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `eventsincidentdata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `eventsnetworkdata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |
| `eventspagedata_CL` | [Netskope Data Connector](../connectors/netskopedataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
