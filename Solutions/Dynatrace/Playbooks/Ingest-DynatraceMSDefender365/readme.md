# Ingest-DynatraceMSDefender365
author: Dynatrace

This playbook will ingest Microsoft Defender 365 insights to Dynatrace. You need a valid Dynatrace Tenant and Access Token, the token should have Ingest logs (logs.ingest) scope in order to use the playbook, you will also need to install the [Microsoft Defender 365](https://learn.microsoft.com/en-us/azure/sentinel/connect-microsoft-365-defender) Sentinel connector to make use of this playbook. To learn more about the Dynatrace platform [Start your free trial](https://www.dynatrace.com/trial)

** Post Install Notes:**

The Logic App creates and uses a Managed System Identity (MSI). 

Assign RBAC 'Microsoft Sentinel Reader' role to the Logic App at the Resource Group level of the Log Analytics Workspace.

## Initial Setup

Logic App is utilitzed by Automation rules. You must setup an Automation rule. Go to the Automation Rules blade in Azure Sentinel. 

If you have not set permissions yet, [review here](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#permissions-for-automation-rules-to-run-playbooks)