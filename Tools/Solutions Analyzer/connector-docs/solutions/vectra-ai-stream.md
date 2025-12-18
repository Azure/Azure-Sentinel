# Vectra AI Stream

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Vectra AI |
| **Support Tier** | Partner |
| **Support Link** | [https://www.vectra.ai/support](https://www.vectra.ai/support) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Last Updated** | 2024-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [AI Vectra Stream via Legacy Agent](../connectors/aivectrastream.md)

**Publisher:** Vectra AI

### [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md)

**Publisher:** Vectra AI

The Vectra AI Stream connector allows to send Network Metadata collected by Vectra Sensors accross the Network and Cloud to Microsoft Sentinel

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Vectra AI Stream configuration**: must be configured to export Stream metadata in JSON

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on parsers based on a Kusto Function to work as expected which are deployed as part of the Microsoft Sentinel Solution.

>**IMPORTANT:** Vectra AI Stream connector is only available for **Linux** agents with **syslog-ng**. Make sure that syslog-ng is installed!

 In the first part, we are going to create the custom tables requires for this solution (using an ARM template). Then we are going to configure the Data Connector.
**Please proceed with these steps:**

**Step 1. Create custom  tables in Log Analytic Workspace (ARM Template)**

  1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fvectranetworks%2FMicrosoft_Sentinel%2Fmain%2FStream%2FAMA%2FARM_Templates%2Fazuredeploy_CustomTables_connector.json)
2. Provide the required details such as the resource group and Microsoft Log Analytics Workspace (**the workspace must exist!**)
4. Click **Review + Create** to deploy.

	_Note: Once deployed, you must be able to see the custom tables in your Log Analytic Workspace (Settings ---> Tables)._

  **Step 2. Install the Syslog via AMA Data connector**

  _Note: This is only required if it has not been install yet in Microsoft Sentinel._
1. Microsoft Sentinel workspace ---> Content Management ---> Content Hub.

2. Search for 'Syslog' (Provider is Microsoft) and select it.

3. Check 'Install' buton on the bottom of the right panel.

  **Step 3. Configure the Syslog via AMA data connector**

  _Note: Two different Data Collection Rules (DCR) are going to be created during this step_
1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector.

2. Search for 'Syslog via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs: LOG_USER/LOG_NOTICE and LOG_LOCAL0/LOG_NOTICE.

4. Create a first DCR (Data Collection Rule). Specify a name. Then, in the Resources tab, select the instance where AMA is going to run. In the Collect tab, select LOG_USER/LOG_NOTICE.

5. Create a second DCR. Specify a different name. Then, in the Resources tab, choose the same host. In the Collect tab, select LOG_LOCAL0/LOG_NOTICE



	Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy.

In the next section, we are goning to modify the syslog-ng configuration that has been created where the AMA is deployed. Then, we are going to modify the DCR configuration to be able to sent the network metadata from Vectra Stream to different custom tables.
**Please proceed with these steps:**

**Step 1. Modify the syslog-ng configuration**

  _Note: A DCR cannot have more than 10 output flows. As we have 16 custom tables in this solution, we need to split the traffic to two DCR using syslog-ng._
1. Download the modified syslog-ng configuration file: [azuremonitoragent-tcp.conf](https://raw.githubusercontent.com/vectranetworks/Microsoft_Sentinel/main/Stream/AMA/syslog-ng/azuremonitoragent-tcp.conf).
2. Log into the instance where syslog-ng/AMA is running.
3. Browse to /etc/syslog-ng/conf.d/  and replace the content of _azuremonitoragent-tcp.conf_ file with the one that you just downloaded.
4. Save and restart syslog-ng (_systemctl restart syslog-ng_).

  **Step 2. Modify the Data Collection rules configuration**

  _Note: The Data Collection Rules that have been created are located in Azure Monitor (**Monitor ---> Settings ---> Data Collection Rules**)_
 1. Locate the 2 DCR that you created in Microsoft Sentinel.
 2. Open the first DCR where Syslog facility is LOG_USER. Then go to Automation ---> Export template ---> Deploy --> Edit template.
 3. Download the dataFlows configuration for LOG_USER DCR: [Stream_DataFlows_dcr1.json](https://raw.githubusercontent.com/vectranetworks/Microsoft_Sentinel/main/Stream/AMA/dcr/Stream_DataFlows_dcr1.json) and find/replace the destination placeholder '<WORKSPACE_NAME>' with your workspace name.
 4. Locate the dataFlows section in the template (Azure Monitor) and replace it with the content of the configuration you downloaded.
 5. In the same DCR, locate the key: resources -> properties -> destinations -> name and replace 'DataCollectionEvent' with the name of the Log Analytics Workspace (same as step 3).
 6. Save --> Review + Create --> Create.
 7. Open the second DCR than you created (Facilily is LOG_LOCAL0) and edit the template (Automation ---> Export template ---> Deploy --> Edit template).
 8. Download the dataFlows configuration for LOG_LOCAL0 DCR: [Stream_DataFlows_dcr2.json](https://raw.githubusercontent.com/vectranetworks/Microsoft_Sentinel/main/Stream/AMA/dcr/Stream_DataFlows_dcr2.json) and find/replace the destination placeholder '<WORKSPACE_NAME>' with your wokrspace name.
 9. Locate the dataFlows section in the template (Azure Monitor) and replace it with the content of the configuration you downloaded.
 10. In the same DCR, locate the key: resources -> properties -> destinations -> name and replace 'DataCollectionEvent' with the name of the Log Analytics Workspace.
 11. Save --> Review + Create --> Create.

**2. Configure Vectra AI Stream**

Configure Vectra AI Brain to forward Stream metadata in JSON format to your Microsoft Sentinel workspace via AMA.

From the Vectra UI, navigate to Settings > Stream and Edit the destination configuration:

 1. Select Publisher: RAW JSON
 2. Set the server IP or hostname (which is the host whhere AMA is running)
 3. Set all the port to **514**.
 4. Save.

**3. Run the following command to validate (or set up) that syslog-ng is listening on port 514**

| | |
|--------------------------|---|
| **Tables Ingested** | `vectra_beacon_CL` |
| | `vectra_dcerpc_CL` |
| | `vectra_dhcp_CL` |
| | `vectra_dns_CL` |
| | `vectra_http_CL` |
| | `vectra_isession_CL` |
| | `vectra_kerberos_CL` |
| | `vectra_ldap_CL` |
| | `vectra_ntlm_CL` |
| | `vectra_radius_CL` |
| | `vectra_rdp_CL` |
| | `vectra_smbfiles_CL` |
| | `vectra_smbmapping_CL` |
| | `vectra_smtp_CL` |
| | `vectra_ssh_CL` |
| | `vectra_ssl_CL` |
| | `vectra_x509_CL` |
| **Connector Definition Files** | [template_VectraStreamAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Data%20Connectors/template_VectraStreamAma.json) |

[→ View full connector details](../connectors/vectrastreamama.md)

## Tables Reference

This solution ingests data into **19 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `VectraStream` | [AI Vectra Stream via Legacy Agent](../connectors/aivectrastream.md) |
| `VectraStream_CL` | [AI Vectra Stream via Legacy Agent](../connectors/aivectrastream.md) |
| `vectra_beacon_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_dcerpc_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_dhcp_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_dns_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_http_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_isession_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_kerberos_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_ldap_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_ntlm_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_radius_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_rdp_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_smbfiles_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_smbmapping_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_smtp_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_ssh_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_ssl_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |
| `vectra_x509_CL` | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) |

[← Back to Solutions Index](../solutions-index.md)
