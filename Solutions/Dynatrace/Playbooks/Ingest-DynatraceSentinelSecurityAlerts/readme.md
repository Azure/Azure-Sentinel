# Ingest-DynatraceSentinelSecurityAlerts
author: Dynatrace

This playbook will Report all Microsoft Sentinel Security Alerts to Dynatrace. You need a valid Dynatrace tenant with [Application Security](https://www.dynatrace.com/support/help/how-to-use-dynatrace/application-security) enabled, you will also need to install the relevant Microsoft Sentinel Connectors which would generated security alerts consumed by this playbook. To learn more about the Dynatrace platform [Start your free trial](https://www.dynatrace.com/trial)

** Prerequisites ** 
- Follow [these instructions](https://www.dynatrace.com/support/help/get-started/access-tokens#create-api-token) to generate a Dynatrace access token, the token should have Ingest logs (logs.ingest) scope.
- [Important step]Store the Dynatrace Access Token as a [secret in Azure Key vault](https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-portal) and provide the key vault name during playbook deployment, by convention the secret name should be 'DynatraceAccessToken'.

** Post Install Notes:**

The Logic App uses a Managed System Identity (MSI). 

Assign RBAC 'Microsoft Sentinel Reader' role to the Logic App at the Resource Group level of the Log Analytics Workspace.

Assign access policy on key vault for Playbook to fetch the secret key

## Initial Setup

A Microsoft Sentinel playbook is utilized by automation rules, therefore to automatically trigger this playbook you must setup a new automation rule. If you have not set permissions yet, [review here](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#permissions-for-automation-rules-to-run-playbooks)

Basic steps for setup of the playbook and automation rule are as follows :

1. Go to the Automation blade in Microsoft Sentinel.
2. Create a new playbook from the 'Ingest Microsoft Sentinel Security Alerts into Dynatrace' [playbook template](https://learn.microsoft.com/en-us/azure/sentinel/use-playbook-templates)
- KeyvaultName: The name of the keyvault created as pre-requisite
- DynatraceTenant: xyz.dynatrace.com
3. Create a new [automation rule](https://learn.microsoft.com/en-us/azure/sentinel/create-manage-use-automation-rules)
- Name : Ingest Microsoft Sentinel Security Alerts into Dynatrace
- Trigger : When alert is created
- Conditions : If Analytic rule name contains 'Dynatrace Application Security - Attack detection'
- Actions : Run playbook IngestDynatraceSentinelSecurityAlerts