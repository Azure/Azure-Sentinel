
# Microsoft Sentinel CrowdSec CTI PlayBook

## Summary

This PlayBook / Logic App automatically create an alert when a successful login is performed from a suspicious or malicious IP.

![Example Alert](Images/alert.png)

## Prerequisites

Before deploying this playbook, ensure the following prerequisites are completed:
   1. Create a CTI API Key on https://app.crowdsec.net/ according to [our documentation](https://docs.crowdsec.net/u/cti_api/api_getting_started/)
   2. Note down the following required value from the console
      - CrowdSec CTI API Key

# Deployment Instructions

1. Click the Deploy to Azure button below to launch the ARM Template deployment wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fbuixor%2Fcrowdsec-sentinel-playbook%2Frefs%2Fheads%2Fmain%2Fazuredeploy.json)

2. Fill in the required parameters.

![Deploy](Images/setup.png)

# Post Deployment Instructions

## Permissions

 - In the resource group, via IAM, grant:
    - "Microsoft Sentinel Contributor" role to the Logic App
    - "Microsoft Sentinel Automation Contributor" role to "Azure Security Insights"
 - Allow Azure Sentinel API Connection (General -> Edit API Connection)

## Example Usage

In our example, we are going to create an **Analytics Rule** to trigger on successful EntraID authentications, and use an **Automation Rule** to trigger our **Logic App**.

Our **Logic App** will exploit CrowdSec's CTI to create an **Alert** if the authentication came from a malicious or suspicious IP.

1. Create Analytics Rule

![Analytics Rule Creation](Images/analytics-rule.png)

2. Create Automation Rule

![Automation Rule Creation](Images/automation-rule.png)

3. Test it

Try to connection from ie. Tor IP Address, wait for your analytics rule to trigger and watch the alerts appear.

