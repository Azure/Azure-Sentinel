# Define, Track, and Complete Key Deployment and Migration Tasks
Author: Matt Lowe

This watchlist is meant to be used in tandem with the Deployment and Migration workbook within the Microsoft Sentinel WOrkbook Gallery or GitHub repository. This watchlist assists with defining, tracking, and completing the key actions during a Microsoft Sentinel deployment/migration. It is a key resource for the solution so please make sure to deploy it. 

## **Pre-requisites**

To deploy, users will need:
1. An Azure Subscription.
2. An Microsoft Sentinel workspace and instance.
3. A user that has Microsoft Sentinel Contirbutor permissions on the Resource Group that Microsoft Sentinel is located in and the name of the workspace that this watchlist should be tied to.
Note: If deploying any Microsoft Defender or Azure Active Directory connector, Global Administrator or Security Administrator will be needed at the tenant level.

## **Deployment Process**
## Option 1
1. Click on the "Deploy to Azure" button.
2. Once in the Azure Portal, select the Subscription and Resource Group that Microsoft Sentinel is under and the name of the workspace that this watchlist should be tied to.
3. Click "Review and Create".
4. Click "Create".
5. Within a minute or two, the template should deploy and the Watchlist should appear within the Microsoft Sentinel environment. 

## Option 2
1. Enter the template within the GitHub folder.
2. In the top right corner, select Raw.
3. Copy the raw text within the template.
4. Go to the Azure Portal.
5. Within the search bar at the top, type "Deploy" and select "Deploy a custom template".
6. Select "build my own template".
7. Within the template space, paste the text copied from GitHub.
8. Select the Subscription and Resource Group that Microsoft Sentinel is under.
9. Click "Review and Create".
10. Click "Create".
11. Within a minute or two, the template should deploy and the Watchlist should appear within the Microsoft Sentinel environment. 

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FWatchlists%2FDeploymentandMigration%2Fazuredeploy.json)