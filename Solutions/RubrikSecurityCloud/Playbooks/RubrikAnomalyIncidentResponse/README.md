# RubrikAnomalyIncidentResponse

## Summary

This playbook provides an end to end example of the collection of Ransomware Anomaly information from Rubrik, its enrichment with Data Classification insights (to aid in incident prioritization), and the options to optionally perform various recovery operations. It uses several other playbooks defined in this solution to perform these tasks.

### Prerequisites

1. The Rubrik Security Cloud data connector should be configured to send appropriate events to Microsoft Sentinel.
2. The Rubrik Security Cloud solution should be configured to [connect to Rubrik Security Cloud API end points using a Service Account](https://docs.rubrik.com/en-us/saas/saas/polaris_api_access_with_service_accounts.html), the service account should be assigned a role that includes the relevant privileges necessary to perform the desired operations (see [Roles and Permissions](https://docs.rubrik.com/en-us/saas/saas/common/roles_and_permissions.html) in the Rubrik Security Cloud user guide).
3. Obtain Teams group id and channel id.
4. Make sure that below mentioned playbooks are deployed before deploying RubrikAnomalyIncidentResponse playbook:
    * RubrikDataObjectDiscovery
    * RubrikAnomalyAnalysis
    * RubrikFilesetRansomwareDiscovery
    * RubrikRansomwareDiscoveryAndFileRecovery
    * RubrikRansomwareDiscoveryAndVMRecovery

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here
    * API Hostname: Hostname of the RubrikApi instance
    * Teams Group Id: Id of the Teams Group where the adaptive card will be posted
    * Teams Channel Id: Id of the Teams Channel where the adaptive card will be posted

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikAnomalyIncidentResponse%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikAnomalyIncidentResponse%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection like teams, microsoft sentinel.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, analytical rules should be configured to trigger an incident. An incident should have the *ClusterId* - custom entity that contains clusterId of an event generated in rubrik, *ObjectId* - custom entity that contains objectId of an event generated in rubrik, *ObjectType* - custom entity that contains objectType of an event generated in rubrik, *ObjectName* -custom entity that contains objectName of an event generated in rubrik . It can be obtained from the corresponding field in Rubrik Anomaly Event logs. Check the [documentation](https://docs.microsoft.com/azure/sentinel/surface-custom-details-in-alerts) to learn more about adding custom entities to incidents.
2. Configure the automation rules to trigger the playbook.
