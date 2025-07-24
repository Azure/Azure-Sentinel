# Rubrik Update Anomaly Status Via Incident

## Summary

This playbook queries Rubrik Security Cloud to enrich the Anomaly event with additional information and internally calls RubrikUpdateAnomalyStatus playbook with additional anomaly information to resolve the anomaly.

### Prerequisites

1. The Rubrik Security Cloud data connector should be configured to send appropriate events to Microsoft Sentinel.
2. The Rubrik Security Cloud solution should be configured to [connect to Rubrik Security Cloud API end points using a Service Account](https://docs.rubrik.com/en-us/saas/saas/polaris_api_access_with_service_accounts.html), the service account should be assigned a role that includes the relevant privileges necessary to perform the desired operations (see [Roles and Permissions](https://docs.rubrik.com/en-us/saas/saas/common/roles_and_permissions.html) in the Rubrik Security Cloud user guide).
3. Rubrik custom connector needs to be deployed prior to the deployment of this playbook, in the same resource group and region. Relevant instructions can be found in the connector doc page.
4. Store Service account credentials in Key Vault and obtain keyvault name and tenantId
    a. Create a Key Vault with unique name
    b. Go to KeyVault -> secrets -> Generate/import and create 'Rubrik-AS-Int-ClientId' & 'Rubrik-AS-Int-ClientSecret' for storing client_id and client_secret respectively
5. Make sure that RubrikUpdateAnomalyStatus playbook is deployed before deploying RubrikUpdateAnomalyStatusViaIncident playbook.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * PlaybookName: Enter the playbook name here.
    * API Hostname: Hostname of the RubrikApi instance
    * Rubrik Connector name: Name of the Rubrik Custom Connector deployed previously
    * keyvaultname: Name of keyvault where secrets are stored.
    * tenantId: TenantId where keyvault is located.
    * UpdateAnomalyStatusPlaybookName: Playbook name which is deployed as part of prerequisites

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikUpdateAnomalyStatusViaIncident%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikUpdateAnomalyStatusViaIncident%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection like keyvault.

1. Click the connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Assign Role to close incident
Assign role to this playbook.   
1. Go to Log Analytics Workspace → <your workspace> → Access Control → Add
2. Add role assignment
3. Assignment type: Job function roles -> Add 'Microsoft Sentinel Contributor' as a Role
4. Members: select managed identity for assigned access to and add your logic app as member
5. Click on review+assign

#### c. Configurations in Microsoft Sentinel
1. In Microsoft sentinel, analytical rules should be configured to trigger an incident which has Entities Mapping available for IP.
2. To manually run the playbook on a particular incident follow the below steps:
   a. Go to Microsoft Sentinel -> <your workspace> -> Incidents
   b. Select an incident.
   c. In the right pane, click on Actions, and from the dropdown select the 'Run Playbook' option.
   d. Click on the Run button beside this playbook.
   
#### d. Configurations in Microsoft Sentinel
1. In Microsoft Sentinel, analytical rules should be configured to trigger an incident. An incident should have the *ClusterId* - custom entity that contains clusterId of an event generated in rubrik, *ObjectId* - custom entity that contains objectId of an event generated in rubrik, *ObjectType* - custom entity that contains objectType of an event generated in rubrik, *ObjectName* -custom entity that contains objectName of an event generated in rubrik . It can be obtained from the corresponding field in Rubrik Anomaly Event logs. Check the [documentation](https://docs.microsoft.com/azure/sentinel/surface-custom-details-in-alerts) to learn more about adding custom entities to incidents.
2. Configure the automation rules to trigger the playbook.
