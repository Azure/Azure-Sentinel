# Rubrik IR Violation

## Summary

This playbook is triggered by a Microsoft Sentinel incident raised for a Rubrik Identity Resilience (IR) violation. It reads the violation ID from the incident and retrieves the latest violation details from Rubrik Security Cloud. It then posts a formatted notification to a SOC Microsoft Teams channel, adds a matching comment to the incident, and sets the violation status to `IN_PROGRESS` in Rubrik.

### Flow detail

1. **Read the violation ID** — the incident's alert Custom Details are parsed and `ViolationId` is read. If it is missing, the playbook comments on the incident and terminates.
2. **Authenticate** — the RSC service-account credentials are read from Key Vault and exchanged for a bearer token through the Rubrik custom connector.
3. **Get the violation** — `policyViolation` is queried with `policyTypes: [POLICY_TYPE_IDENTITY, POLICY_TYPE_IDP, POLICY_TYPE_IDENTITY_EVENT]`. The playbook extracts `violationSeverity`, `status`, `policy.name`, `policy.description`, `policy.policyType`, `policy.manualRemediationProcess` and, from `resourceMetadata.metadata`, the `displayName`, `userPrincipalName`, `idpType`, `domainName`, `principalType`, `privilegeType` and `title`.
4. **Notify the SOC in Teams** — a formatted message is posted to the configured channel carrying the violation ID, severity, identity display name and email, policy name, policy type, IdP type, the manual remediation steps returned by RSC, and a direct link to the Sentinel incident.
5. **Update the violation** — `bulkUpdatePolicyViolations` sets `POLICY_VIOLATION_STATUS_IN_PROGRESS`, and a matching comment is added to the incident.

> **Note:** the identity is **not** notified by email. The notification goes to the SOC Teams channel configured by `TeamsGroupId` / `TeamsChannelId` so an analyst can act on the manual remediation steps. There is no Send Email action and no Office 365 Outlook connection in this template.

### Prerequisites

1. The Rubrik Security Cloud data connector should be configured to send appropriate events to Microsoft Sentinel.
2. The Rubrik Security Cloud solution should be configured to [connect to Rubrik Security Cloud API end points using a Service Account](https://docs.rubrik.com/en-us/saas/saas/polaris_api_access_with_service_accounts.html), the service account should be assigned a role that includes the relevant privileges necessary to read and update policy violations (see [Roles and Permissions](https://docs.rubrik.com/en-us/saas/saas/common/roles_and_permissions.html) in the Rubrik Security Cloud user guide).
3. Rubrik custom connector needs to be deployed prior to the deployment of this playbook, in the same resource group and region. Relevant instructions can be found in the connector doc page.
4. Store Service account credentials in Key Vault and obtain the keyvault name.
    a. Create a Key Vault with a unique name.
    b. Go to KeyVault -> secrets -> Generate/import and create 'Rubrik-AS-Int-ClientId' & 'Rubrik-AS-Int-ClientSecret' for storing client_id and client_secret respectively.
5. Obtain the Teams group id and channel id where the SOC notification will be posted.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * PlaybookName: Enter the playbook name here.
    * API Hostname: Hostname of the Rubrik Security Cloud instance (e.g. customer.my.rubrik.com), without scheme or trailing slash.
    * Rubrik Connector name: Name of the Rubrik Custom Connector deployed previously.
    * KeyVaultName: Name of the keyvault where secrets are stored.
    * TeamsGroupId: Id of the Teams Group where the SOC notification will be posted.
    * TeamsChannelId: Id of the Teams Channel where the SOC notification will be posted.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikIRViolation%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikIRViolation%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection: Rubrik custom connector, Microsoft Teams, Key Vault and Microsoft Sentinel.

1. Click the connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Assign roles to the playbook

Assign roles to this playbook's managed identity.

1. Go to Log Analytics Workspace → <your workspace> → Access Control → Add
2. Add role assignment
3. Assignment type: Job function roles -> Add 'Microsoft Sentinel Responder' as a Role
4. Members: select managed identity for assigned access to and add your logic app as member
5. Click on review+assign
6. Grant the playbook's managed identity the 'Key Vault Secrets User' role (or a get-secret access policy) on the Key Vault named by the KeyVaultName parameter.

#### c. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, analytical rules should be configured to trigger an incident. An incident should have the *ViolationId* - custom detail that contains the identity violation id generated in Rubrik. It can be obtained from the corresponding field in Rubrik IR Violation event logs. Check the [documentation](https://docs.microsoft.com/azure/sentinel/surface-custom-details-in-alerts) to learn more about adding custom details to incidents. `ViolationId` is the only Custom Detail this playbook requires.
2. Configure the automation rules to trigger the playbook.

### Error handling

Each RSC call checks both the HTTP status code and the presence of a non-empty `errors` key, because RSC returns GraphQL errors with HTTP 200.

| Failure point | Behaviour |
|---------------|-----------|
| `ViolationId` missing from the incident | Comment on incident, terminate |
| Authentication | Comment on incident, terminate |
| Get IR Violation | Comment on incident, terminate |
| Update violation status | Comment on incident, terminate |
