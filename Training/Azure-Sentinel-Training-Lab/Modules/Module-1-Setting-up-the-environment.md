# Module 1 - Setting up the environment

#### 🎓 Level: 100 (Beginner)
#### ⌛ Estimated time to complete this lab: 20 minutes

## Objectives

This module guides you through the deployment of the Azure Sentinel environment that will be used in all subsequent modules.

#### Prerequisites

To get started with Azure Sentinel, you must have a Microsoft Azure subscription. If you do not have a subscription, you can sign up for a free account.

Permissions to create a resource group in your Azure subscription. 

### Exercise 1: Deploy Azure Sentinel Labs ARM template

1. Click on the button below. Make sure that you open it in a new tab so you keep these instructions open.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTraining%2FAzure-Sentinel-Training-Lab%2FArtifacts%2Fazuredeploy.json)

2. Fill out the defferent fields:
    - **Subscription**: choose the Azure subscription where you would like to deploy the Azure Sentinel lab
    - **Resource Group**: select an existing resource group or create a new resource group (recommended) that will host the lab resources
    - **Region**: from the drop down, select the Azure region where the lab will be located
    - **Workspace Name**: provide a name for the Azure Sentinel workspace. Please note that the workspace name should include 4-63 letters, digits or '-'. The '-' shouldn't be the first or the last symbol

![setup1](../Images/setup_1.png)


3. Click **Review + create** and then **Create** in the next screen. The deployment will start and should take around **15 minutes** to complete. You should see this screen when it finishes.

![setup3](../Images/setup_3.png)


4. Once finished, go to the search bar at the top and type "sentinel", then click on Azure Sentinel .

![setup4](../Images/setup_4.png)


5. Choose the workspace name that you selected in step #2. 

![setup5](../Images/setup_5.png)

6. Congratulations! You have now deployed your Azure Sentinel lab 😊. Your screen should like this:

![setup6](../Images/setup_6.png)

### Exercise 2: Configure Azure Sentinel Playbook

In this exercise, we will configure a Playbook that will be later used in the lab. This will allow the playbook to access Sentinel.

1. Navigate to the resource group where the lab has been deployed.

2. In the resource group you should see an API Connection resource called **azuresentinel-Get-GeoFromIpAndTagIncident**, click on it.

![playbook1](../Images/playbook1.png)

3. Click on Edi **API connection** under **General**.

![playbook2](../Images/playbook2.png)

4. Click on **Authorize** and a new window will open to chose an account. Pick the user that you want to authenticate with. This should normally be the same user that you're logged in with.

![playbook3](../Images/playbook3.png)

5. Click **Save**.

![playbook4](../Images/playbook4.png)

**Congratulations, you have completed Module 1!**. You can now continue to **[Module 2 - Data Connectors](./Module-2-Data-Connectors.md)**