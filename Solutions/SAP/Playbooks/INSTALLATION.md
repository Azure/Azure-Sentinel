# Step-by-Step Installation Guide

< 🏡[home](README.md)

[🪂Custom Azure Deployment Wizard](https://portal.azure.com/?feature.customportal=false#create/Microsoft.Template)

| Playbook | Description |
| --- | --- |
| [Lock SAP User from Teams - Basic](./Basic-SAPLockUser-STD/) | Basic playbook with minimum integration effort for simple SAP user blocking on ERP via SOAP service |
| [Remediate SAP Sentinel Collector Agent attack](./SAPCollectorRemediate-STD/) | Sophisticated scenario distinguishing between SAP maintenance events and malicious deactivation of the audit log ingestion into Sentinel using [Azure Center for SAP Solutions (ACSS)](https://learn.microsoft.com/azure/sap/center-sap-solutions/overview) health APIs |

Find out more from our blog series [here](https://blogs.sap.com/2023/05/22/from-zero-to-hero-security-coverage-with-microsoft-sentinel-for-your-critical-sap-security-signals-blog-series/).

The deployment process first creates the infrastructure and generates the IDs for the managed identity of your logic app (Standard). Due to that a two-step deployment is required to add the required Connections for your workflow.

> **Note**: the templates are self-contained and therefore assume that no app service plan, connections or any other sharable Azure resources are available yet. Adjust the references to your liking where needed. Especially the app service plan is often used most efficiently and economically if it powers multiple workflows.

## Create Logic App (Standard) infrastructure

1. Choose "Custom deployment" from the Azure Portal or above link.
2. Click "Build your own template in the editor" and paste the content of the ´azuredeploy.json´ file of your desired playbook folder.

> **Note**: skip steps 1-2 if using the "Deploy to Azure button"

3. Fill in the required parameters and click "Review + create".
4. Click "Create" to deploy the ARM template for the Logic Apps infrastructure.
5. After the deployment is finished, navigate to **Outputs pane** and grab the values for `logicAppSystemAssignedIdentityTenantId` and `logicAppSystemAssignedIdentityObjectId`.

## Add Connections for the workflow

[🪂Custom Azure Deployment Wizard](https://portal.azure.com/?feature.customportal=false#create/Microsoft.Template)

### Create Connections objects

6. Create a second deployment again using the custom [deployment link](https://portal.azure.com/?feature.customportal=false#create/Microsoft.Template) or the "Deploy to Azure button" to add the required Connections. Provide the values from step 5.
7. After the deployment is finished, navigate to **Outputs pane** and grab the values for the runtime URLs of your Connections. Alternatively, grab the URLs from the newly created API Connection resource (General -> Properties -> Connection Runtime URL)
8. Navigate to the created Connections, open every one and click `Edit API connection`, authorize and save.

### Connect Logic App (Standard) to the new Connections

9. Choose `JSON` view from the Overview section of the Connection resource and copy the `id` from the root scope and the id under properties -> api.
10. Navigate to the Connections section (under workflows) of your Logic App and open the JSON view.
11. Past the content of the `connections.json` file of your desired playbook folder, supply the runtime URLs taken in step 7, supply the root id under connection -> id, and the api id to the api -> id field. Find the connections.json file from above table.

### Add required Azure Roles to the Logic App (Standard) managed identity

12. Navigate to the Identity section (under Settings) of your Logic App, choose the `System Assigned` tab, click `Azure role assignments`, and add the required roles mentioned for your scenario (see [here](./Basic-SAPLockUser-STD/README.md#required-azure-roles) for instance) at least on resource group level, where Sentinel and the associated Log Analytics Workspace are deployed.
13. Verify from the API Connections tab that the Connections are in Status "Connected".

## Add the workflow parameters to the Logic App (Standard)

14. Navigate to the Logic App and open the `Parameters` view under "Workflows".
15. Paste the content of the `workflowparameters.json` file of your desired playbook folder. Find the file from above table. Maintain your values as described on the [blog series](https://blogs.sap.com/2023/05/22/from-zero-to-hero-security-coverage-with-microsoft-sentinel-for-your-critical-sap-security-signals-youre-gonna-hear-me-soar-part-1/). Save the parameters.

## Add the workflow to the Logic App (Standard)

16. Navigate to the Logic App and create a new workflow of type `Stateful`.
17. Open the `Code` view, discard default json, and paste the content of the `workflow.json` file of your desired playbook folder. Find the file from above table.
18. Save the playbook.

## Configure Azure VNet integration

To reach the private SAP network, the Logic App (Standard) needs to be integrated into the Azure VNet, where the SAP system is located.

19. Navigate to the Logic App and open the `Settings` section.
20. Click `Networking` and `Configure VNet integration` from the "Outbound Traffic" pane.

## Configure Access Restrictions to the Logic App (Standard)

21. Navigate to the Logic App and open the `Settings` section.
22. Click `Networking` and configure `Access restriction` from the "Inbound Traffic" pane. Use the button ´+ Add´ under "Site access and rules" -> "Main site". Choose "Unmatched rule action" Allow and the service tag "Azure Sentinel" from the dropdown menu.

Your Logic App can now only be triggered from Sentinel!

> **Warning**
> The Logic App designer access from your location will now block insights into its processing, because of above access restriction. Consider to add your location, development jumpbox, Azure Bastion or VPN access to the VNet hosting SAP, etc. to the access restriction.

23. Navigate to the Incidents section of Microsoft Sentinel and identify an SAP incident.
24. Click `Actions`, choose `Run playbook`, choose your new Logic App (Standard), and click `Run` to trigger an integration test.

> **Note**
> Make sure Sentinel is allowed to call your new Logic App. Navigate to the `Manage Permissions` pane from Sentinel -> Configuration -> Settings -> Settings -> Playbook Permissions -> Configure Permissions -> Choose your resource group -> Click Apply.

25. Verify execution from the Logic App (Standard) run history. Find it on the workflow Overview section.

## Dynamic vs. Static parameters on the Logic App

For simplicity and ease of configuration the basic playbooks offer the possibility to maintain parameters like the API base path to the SAP SOAP service for the user lock from the Logic App UI experience. This is done by using the `workflowparameters.json` file. The downside of this approach is that the Logic App needs to be redeployed/duplicated, if the API base path changes.

For enterprise scale, use the provided fields on the SAP watchlist `SAP - Systems`. The column is called "InterfaceAttributes". See [part 2 of the blog series](https://blogs.sap.com/2023/05/23/from-zero-to-hero-security-coverage-with-microsoft-sentinel-for-your-critical-sap-security-signals-part-2/) for more details.

[🔝](#)
