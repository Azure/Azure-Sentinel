# Tanium-CloseTHRAlert

## Overview
This playbook will close any associated alerts in Tanium Threat Response that may also have a corresponding incident in Sentinel. Triggering this playbook will send a request to the Tanium Forwarder (a program running outside of Microsoft Sentinel) which will talk directly to Tanium to close any alerts.  

## Prerequisites
Alerts from Tanium Threat Response will not trigger an incident in Microsoft Sentinel without "Tanium Threat Response Alerts" analytic rule. Without this rule, this playbook will not have the desired effect.

## Post-Deployment Instructions
After deploying the playbook, you must authorize the connections leveraged.

1. Visit the playbook resource.
2. Under "Development Tools" (located on the left), click "API Connections".
3. Ensure each connection has been authorized.

## Note
With the default deployment and configuration settings of the playbooks, your API-Key is exposed in plain text. All the users who have read access to the playbooks (logic apps) can view your API-Key.
If you do not want to expose the API-Key in plain text, then it is advised to store API-Key with the azure key-vault and playbook integration. Please refer following links for more details [Secure access and data - Azure Logic Apps | Microsoft Docs](https://docs.microsoft.com/en-us/azure/logic-apps/logic-apps-securing-a-logic-app?tabs=azure-portal#secure-inputs-and-outputs-in-the-designer).
