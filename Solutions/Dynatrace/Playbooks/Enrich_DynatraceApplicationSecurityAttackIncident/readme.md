# Enrich_DynatraceApplicationSecurityAttackIncident
author: Dynatrace

This playbook uses the Dynatrace REST APIs to automatically enrich incidents created by Microsoft Sentinel. You need a valid Dynatrace Tenant and Access Token, the token should have Read attacks (attacks.read) scope in order to use the playbook. To learn more about the Dynatrace platform [Start your free trial](https://www.dynatrace.com/trial)

** Post Install Notes:**

The Logic App creates and uses a Managed System Identity (MSI) to update the Microsoft Sentinel Incident. 

Assign RBAC 'Microsoft Sentinel Responder' role to the Logic App at the Resource Group level of the Log Analytics Workspace.

## Initial Setup

Logic App is utilitzed by Automation rules. You must setup an Automation rule. Go to the Automation Rules blade in Azure Sentinel. 

If you have not set permissions yet, [review here](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#permissions-for-automation-rules-to-run-playbooks)