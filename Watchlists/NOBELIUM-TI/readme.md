# Ingest and Reference Nobelium Threat Intelligence
Author: Matt Lowe

This Watchlist is meant to host IoC's from the recent NOBELIUM hack. This data can be refernced for threat hunting and analytic rules to ensure that malicious activity has not taken place within the environment. These IoCs were published by the Microsoft Threat Intelligence Center (MSTIC).

https://www.microsoft.com/security/blog/2021/05/27/new-sophisticated-email-based-attack-from-nobelium/


## **Pre-requisites**

To deploy, users will need:
1. An Azure Subscription.
2. An Azure Sentinel workspace and instance.
3. A user that has Azure Sentinel Contirbutor permissions on the Resource Group that Azure Sentinel is located in.

## **Deployment Process**
## Option 1
1. Click on the "Deploy to Azure" button.
2. Once in the Azure Portal, select the Subscription and Resource Group that Azure Sentinel is under.
3. Click "Review and Create".
4. Click "Create".
5. Within a minute or two, the template should deploy and the Watchlist should appear within the Azure Sentinel environment. 

## Option 2
1. Enter the template within the GitHub folder.
2. In the top right corner, select Raw.
3. Copy the raw text within the template.
4. Go to the Azure Portal.
5. Within the search bar at the top, type "Deploy" and select "Deploy a custom template".
6. Select "build my own template".
7. Within the template space, paste the text copied from GitHub.
8. Select the Subscription and Resource Group that Azure Sentinel is under.
9. Click "Review and Create".
10. Click "Create".
11. Within a minute or two, the template should deploy and the Watchlist should appear within the Azure Sentinel environment. 

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FWatchlists%2FNOBELIUM-TI%2Fazuredeploy.json)