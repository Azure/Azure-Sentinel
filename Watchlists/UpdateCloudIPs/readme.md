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
None