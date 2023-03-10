# Ingest M365 Security Insights Data
Author: Matt Lowe, Benjamin Kovacevic

The M365 Security Posture connector template will deploy an Azure Logic App that is configured to ingest data from the different M365D products to highlight the statuses of entities within the environment. The connector calls upon HTTP API to gather this data from the different products, with the products being:
- Microsoft Defender for Endpoint
- Microsoft 365 Defender

Azure Security Center and Microsoft Cloud App Security data will be referenced in the related workbook via the built-in connectors and data ingestion channels.

The connector will be fetching logs such as:
- MDE Secure Score
- MDE Exposure Score
- MDE Recommendations
- MDE Vulnerabilites
- M365 Secure Score

The workbook will also be referencing data from Azure Security Center and Microsoft Cloud App Security such as:
- ASC Secure Score
- ASC Recommendations and Regulatory Compliance
- MCAS ShadowIT

Link to the [Microsoft Defender Security Insights Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Workbooks/M365SecurityPosture.json)

You can find all instructions on the blog post on Microsoft Tech Community - [Microsoft Defender Security Insights in Azure Sentinel](https://techcommunity.microsoft.com/t5/azure-sentinel/microsoft-defender-security-insights-in-azure-sentinel/ba-p/2359705)

## **Pre-requisites**

To deploy, users will need:
1. An Azure Subscription
2. An Azure Sentinel workspace and instance
3. A registered application within Azure Active Directory
4. A user that has Azure Sentinel Contirbutor permissions on the Resource Group that Azure Sentinel is located in

## **Set Up**
First, an application needs to registered in Azure AD and assigned API permissions.
1.	Go to https://aad.portal.azure.com/ <strong>> Azure Active Directory > App registrations > click on +New registration</strong>
2.	Enter name (M365SecurityPosture API) and click on Register
3.	First we need to add 2 permission from Microsoft Graph<br>
- Click on <strong>API permissions</strong> from right menu and then on <strong>+Add a permission</strong>. Select Microsoft Graph and then Application permissions. Search and select following permissions <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i.	SecurityEvents.Read.All<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ii.	SecurityEvents.ReadWrite.All<br>
- Click on Add permission
4.	And now we need to add permissions connected to Microsoft Defender for Endpoint<br>
- Click on <strong>+Add a permission</strong> and click on <strong>APIs my organization use</strong>. Search for <strong>WindowsDefenderATP</strong> and select it. Select Application permissions and then search and select following permissions <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i.	Score.Read.All<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ii.	SecurityRecommendation.Read.All <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;iii.	Vulnerability.Read.All<br>
- Click on Add permission
5.	Click on <strong>Grant admin consent for {name of your organization}</strong>
6.	Next we need to generate Secret. Click on <strong>Certificates & Secrets</strong> from right menu and choose <strong>+New client secret</strong>
7.	Enter description (M365SecurityPosture API Secret), select Never and click on Add
8.	Copy <strong>Value</strong> of the secret – if you don’t copy you’ll need to recreate it – you cannot see it once you leave this view
9.	Now click on Overview from right menu and copy fields <strong>Application (client) ID</strong> and <strong>Directory (Tenant) ID</strong>


Note: The Microsoft Cloud Application Security data connector needs to be on and is ingesting Shadow IT data (Cloud Discovery Logs). If the MCAS data connector isn’t enabled, please follow the public documentation - https://docs.microsoft.com/azure/sentinel/connect-cloud-app-security.

Once the application is ready, as well as <strong>Workspace ID and Workspace key</strong>, the Logic App can be deployed. 

## **Deployment Process**
## **Option 1**
1. Click on the "Deploy to Azure" button.
2. Once in the Azure Portal, select the Subscription and Resource Group that Azure Sentinel is under.
3. Enter the details that are required for the Playbook.
4. Click "Review and Create".
5. Click "Create".
6. Within a minute or two, the template should deploy and the Playbook should appear within the Azure Sentinel environment. 

## **Option 2**
1. Enter the template within the GitHub folder.
2. In the top right corner, select Raw.
3. Copy the raw text within the template.
4. Go to the Azure Portal.
5. Within the search bar at the top, type "Deploy" and select "Deploy a custom template".
6. Select "build my own template in the editor".
7. Within the template space, paste the text copied from GitHub.
8. Select the Subscription and Resource Group that Azure Sentinel is under.
9. Enter the details that are required for the Playbook.
10. Click "Review and Create".
11. Click "Create".
12. Within a minute or two, the template should deploy and the Playbook should appear within the Azure Sentinel environment. 

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FM365-Security-Posture%2Fazuredeploy.json)
