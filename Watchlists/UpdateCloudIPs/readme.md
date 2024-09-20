# Update Cloud IPs Watchlist Function
Author: Nicholas DiCola

 UpdateCloudIPs Azure Function is designed to run every Sunday at 00:00.  The function will create a Watchlist for each cloud provider (Azure, AWS, GCP) and add all of their IP Ranges to the watchlist.  If the watchlist exists, it will compare the current watchlist with the current downloaded ranges. After compare it will add/remove new/old ranges and update expiration date if the range is the same.

Following are the configuration steps to deploy Function App.

## **Pre-requisites**

## Configuration Steps to Deploy Function App
1. Click on Deploy to Azure (For both Commercial & Azure GOV)
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FWatchlists%2FUpdateCloudIPs%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FWatchlists%2FUpdateCloudIPs%2Fazuredeploy.json)
2. Select the preferred **Subscription**, **Resource Group** and **Location**  

## Post Deployment Steps
1. Go to the resource group with the Azure Function.
2. Click the **Azure Function**.
3. Click **Identity** blade under **Settings**.
4. Click **Azure Role Assignments**.
6. Click **Add Role Assignment**.
7. Set **Scope** to **Resource Group**, Select the **Subscription** and **resource group** that contains the **Azure Sentinel** workspace. Set **role** to **Azure Sentinel Contributor**.
8. Add another role assignment this time giving the identity **Reader** permissions at the subscription level.  