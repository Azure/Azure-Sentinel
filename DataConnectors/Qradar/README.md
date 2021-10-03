# ARM templates 
Author: Secugram 
# 1. Project name
Azure Sentinel as new on premise SOAR replacement solution

# 2. Elevator pitch

When we were looking for hackathon ideas, we found that in common deployment scenario, Azure Sentinel just worked as a "complementary" or second SIEM, serving just for cloud environment and the primary SIEM solution is still typical on-premise product such as IBM QRadar or Splunk. Therefore, we want to do in opposite approach that **Sentinel will act as a primary SIEM/SOAR** - a single pane of glass for all security operation programs. Other SIEMs become the second, sending on premise signal data to Sentinel. Azure Sentinel is a new cyberdefense commander for cloud era. 

We think that this idea is a good fit for any enterprises in cloudification journey, when cloud becomes a major workload and the rest is on premise. 

# 3. About the project
## Inspiration

Most of SIEM deployment in our market is IBM QRadar and therefore the most compatible SOAR product is IBM Resilient. But two products are quite complex and the most important thing here they does not support cloud environment natively. 

Besides that, existing solutions for Azure Sentinel integration with IBM QRadar is one way that Sentinel integrates into IBM QRadar. So it is hard for us to leverage SOAR features of Sentinel in most of cases.

Therefore, we are inspired by the idea that Sentinel will become the main SOAR solution for any enterprises despite of any SIEMs they are using. And we can replace IBM Resilient in most cases by just using Azure Sentinel. 

## What it does

- Azure Sentinel ingests the offenses from IBM Qradar SIEM by a custom connector.
- Azure Sentinel displays offense information by a dedicated workbook.
- Azure Sentinel can orchestrate IBM QRadar through AppLogic functions to do common activities such as updating offense statuses, modifying existing rules or changing system configuration. 

## How we built it
- First and foremost, the connector was built using purely Python. Using both Qradar REST API and Azure API to collecting and ingesting Qradar's Offenses.  
- At the beginning, the connector query Qradar REST API for pulling out all offenses in a specific timerange. 
- After that, the connector to Log Analytics Workspace, using Kusto Query Language (KQL) to collect all existed offenses in Log Analytics Workspace.
- Before pushing new events Log Analytics, the connector looping through all offenses collected from QRadar REST API to check whether an offenses existed in Log Analytics or not.
- Finally, the connector pushs new offenses to Log Analytics.

## Challenges we ran into
- Although Microsoft provides a Python developer guide for Azure Functions, running Python code in Azure Functions is not as simple as using Microsoft Powershell. Before deploying to Azure, we must learn how to code, deploy, and test our function locally.
- The second issue we encountered was determining whether or not an offense existed in Log Analytics. To query all of the data in Log Analytics, we need to connect to Log Analytics Workspace using Python. Our mission is to figure out which authentication and authorization mechanisms we can use and how to use them properly, as Microsoft has built quite complex authentication and authorization mechanisms into the Azure environment. Finally, we decide that the Service Principal Name (SPN) is the most efficient way to solve this problem.
- Last but not least, we looked at how to deploy all of our connector's components to Azure. In terms of automation deployments, the ARM template has incredible capabilities. We choose to stick with the ARM template and refactor our code to work with it. Our team created a comprehensive template for deploying our connector in the blink of an eye after troubleshooting and fixing ton of errors during the deployment.
## Accomplishments that we're proud of

- Developing a new custom connector to integrate IBM QRadar offense into Azure Sentinel through Azure Functions.

## What we learned

- How to develop an end-to-end addon for Azure Sentinel from scratch. We love the idea to develop a new Sentinel capability by leveraging cloud native services such as Azure Functions and AppLogic.

## What's next for Azure Sentinel as new on premise SOAR replacement solution

- Develop a predefined playbook sets for automating common SOC analyst tasks such as: updating offense statuses, changing system configuration (updating reference set, adding new detection rules), correlating offense information and other intelligence from Sentinel.

- An full feature addon for replacing IBM Resilient completely.  

# 4. Value add to enterprise

We bring values to enterprise in some below business cases

- Enterprise is looking for a cloud native SOAR solution that can work smoothly with existing IBM QRadar SIEM. And Sentinel is a good solution.

- Enterprise is in cloud transition journey, when they are migrating most of on premise workload to Azure cloud. During that time, they must still use both an on premise IBM QRadar and a cloud native SIEM. They just integrate QRadar into Sentinel. After they finish cloud migration project, they just turn off the legacy SIEM or reduce the workload of on premise SIEM to minimum level. This approach saves huge of effort for another SIEM migration project.

# ARM Template for deployment
1) This template let's you upload the Azure Function which will run daily to import (via API) QRadar offenses into Azure Sentinel workspace

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fhieuttmmo%2Fazure_sentinel_qradar_connector%2Fmain%2Fazuredeploy_QRADARConnector_API_FunctionApp.json)
