# Ingest-DynatraceMSDefender365
author: Dynatrace

This playbook will ingest Microsoft Defender 365 insights to Dynatrace. You need a valid Dynatrace Tenant and Access Token, the token should have Ingest logs (logs.ingest) scope in order to use the playbook, you will also need to install the [Microsoft Defender 365](https://learn.microsoft.com/en-us/azure/sentinel/connect-microsoft-365-defender) Sentinel connector to make use of this playbook. To learn more about the Dynatrace platform [Start your free trial](https://www.dynatrace.com/trial)

** Prerequisites ** 
- Follow [these instructions](https://www.dynatrace.com/support/help/get-started/access-tokens#create-api-token) to generate a Dynatrace access token.
- [Important step]Store the Dynatrace Access Token as a secret in Azure Key vault and provide the key vault name during deployment, by convention the secret name should be 'DynatraceAccessToken'.

** Post Install Notes:**

The Logic App creates and uses a Managed System Identity (MSI). 

Assign RBAC 'Microsoft Sentinel Reader' role to the Logic App at the Resource Group level of the Log Analytics Workspace.

Assign access policy on key vault for Playbook to fetch the secret key

## Initial Setup

Logic App is utilitzed by Automation rules. You must setup an Automation rule. Go to the Automation Rules blade in Azure Sentinel. 

If you have not set permissions yet, [review here](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#permissions-for-automation-rules-to-run-playbooks)