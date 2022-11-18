# Enrich-DynatraceAppSecAttackAADIDPRiskySignins
author: Dynatrace

This playbook will Report Azure Active Directory Identity Protection Risky Sign-ins related to Dynatrace Application Security Attack back to Dynatrace. You need a valid Dynatrace Tenant and Access in order to use the playbook, you will also need to install the [Azure Active Directory Identity Protection](https://learn.microsoft.com/en-us/azure/active-directory/identity-protection/overview-identity-protection) Sentinel connector to make use of this playbook. To learn more about the Dynatrace platform [Start your free trial](https://www.dynatrace.com/trial)

** Post Install Notes:**

Authorize the web.connection APIs deployed into the ResourceGroup.

The Logic App creates and uses a Managed System Identity (MSI) to query the Log Analytics Workspace. 

Assign RBAC 'Log Analytics Reader' role to the Logic App at the Resource Group level of the Log Analytics Workspace.

## Initial Setup

Logic App is utilitzed by Automation rules. You must setup an Automation rule. Go to the Automation Rules blade in Azure Sentinel. 

If you have not set permissions yet, [review here](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#permissions-for-automation-rules-to-run-playbooks)