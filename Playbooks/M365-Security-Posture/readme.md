# Ingest M365 Security Posture Data
Author: Matt Lowe, Benjamin Bovacevic

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

## **Pre-requisites**

To deploy, users will need:
1. An Azure Subscription
2. An Azure Sentinel workspace and instance
3. A registered application within Azure Active Directory
4. A user that has Azure Sentinel Contirbutor permissions on the Resource Group that Azure Sentinel is located in

## **Set Up**
First, an application needs to registered in Azure AD and assigned API permissions.
1.	Go to https://aad.portal.azure.com/ > Azure Active Directory > App registrations > click on +New registration.
2.	Enter a name (SecureScore API) and click on Register.
3.	 These two permissions are needed from Microsoft Graph:
    a.	Click on API permissions from right menu and then on +Add a permission. Select Microsoft Graph and then Application permissions. Search and select SecurityEvents.Read.All and click on Add permission.
    b.	Click on +Add a permission. Select Microsoft Graph and then Application permissions. Search and select SecurityEvents.ReadWrite.All and click on Add permission.
4.	Add permissions need to connect to Microsoft Defender for Endpoint
    a.	Click on +Add a permission and click on APIs my organization use. Search for WindowsDefenderATP and select it. Select Application permissions and then search and select Score.Read.All and click on Add permission.
    b.	Click on +Add a permission and clicA secret for the application needs to be generated. Click on Certificates & Secrets from right menu and choose +New client secret.
7.	Enter description (MCAS Frequent Traveller remediation), select Never and click on Add.
8.	Copy Value of the secret – if the secret is not copied, it cannot be seen once the blade has been left.
9.	Click on Overview from right menu and copy fields Application (client) ID and Directory (Tenant) ID
10.	Go to Azure portal and go to Log Analytics Workspaces. Copy the workspace ID and key.k on APIs my organization use. Search for WindowsDefenderATP and select it. Select Application permissions and then search and select SecurityRecommendation.Read.All and click on Add permission.
    c.	Click on +Add a permission and click on APIs my organization use. Search for WindowsDefenderATP and select it. Select Application permissions and then search and select Vulnerability.Read.All and click on Add permission.
5.	Click on Grant admin consent for {name of your organization}.
6.	

Note: The Microsoft Cloud Application Security data connector needs to be on and is ingesting Shadow IT data (Cloud Discovery Logs). If the MCAS data connector isn’t enabled, please follow the public documentation.

Once the application is ready, as well as Workspace ID and Workspace key, the Logic App can be deployed. 

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