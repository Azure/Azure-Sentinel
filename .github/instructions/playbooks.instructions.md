---
applyTo: "Playbooks/**/*.json,Playbooks/**/*.yaml,Playbooks/**/*.yml"
---

# Playbooks Instructions
---

## Overview

Microsoft Sentinel playbooks are automation workflows built on Azure Logic Apps that help SOC analysts respond to incidents, alerts, and entities. Playbooks can run automatically when certain alerts or incidents occur, or be triggered manually.

---

## Playbook Use Cases

Playbooks address common security operations scenarios:

### Incident Enrichment
- Collect additional data on suspicious entities (IP addresses, user accounts, domains)
- Gather context from external threat intelligence sources
- Enhance alerts with WHOIS lookups, file reputation data, or user information

### SOC Ticketing System Integration
- Synchronize Microsoft Sentinel incidents with ServiceNow, Jira, or other ticketing systems
- Create bidirectional sync for ticket updates
- Automatically close incidents when tickets are resolved

### Automated Response Actions
- Send Teams/Slack messages to security teams for confirmation or awareness
- Block malicious IPs/URLs in firewalls or proxy systems
- Disable compromised user accounts
- Quarantine suspicious files
- Reset user passwords
- Generate compliance reports

---

## Directory Structure

### For Standalone Playbooks
```
Playbooks/
├── [PlaybookName]/
│   ├── azuredeploy.json          (REQUIRED)
│   └── README.md                  (REQUIRED)
```

### For Playbooks with Custom Connectors
```
Solutions/[SolutionName]/Playbooks/
├── CustomConnector/
│   └── [CustomConnectorName]/
│       ├── azuredeploy.json
│       └── README.md
├── [PlaybookName]/
│   ├── azuredeploy.json
│   └── README.md
```

### Directory Naming
- Use descriptive, action-oriented names
- Use PascalCase or kebab-case consistency
- Examples: `EnrichIP`, `SyncToServiceNow`, `BlockUserAccount`

---

## ARM Template Requirements

### Root Level Structure
```
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "metadata": { ... },
  "parameters": { ... },
  "variables": { ... },
  "resources": [ ... ]
}
```

### File Naming
- **Mandatory:** Name the ARM template file `azuredeploy.json`
- Required for automated deployment and solution packaging

### Metadata Section (REQUIRED)
Must include:
- `title` - Playbook display name
- `description` - Clear description of functionality and behavior
- `author` - Object with `name` property
- `support.tier` - "community", "partner", or "microsoft"
- `prerequisites` - Array of prerequisite requirements (e.g., ["None", "permissions needed"])
- `postDeployment` - Array of post-deployment configuration steps
- `lastUpdateTime` - ISO 8601 timestamp (e.g., "2024-04-15T00:00:00.000Z")
- `entities` - Array of entity types (e.g., ["Account", "IP", "URL"])
- `tags` - Array of tags (e.g., ["Remediation", "Response"])
- `releaseNotes` - Array with `version`, `title`, `notes` fields

#### Valid Metadata Example
```json
"metadata": {
  "title": "Block Entra ID user - Incident",
  "description": "For each account entity included in the incident, this playbook will disable the user in Microsoft Entra ID, add a comment to the incident that contains this alert and notify manager if available. Note: This playbook will not disable admin user!",
  "prerequisites": [
    "None"
  ],
  "postDeployment": [
    "1. Assign Microsoft Sentinel Responder role to the Playbook's managed identity.",
    "2. Grant User.Read.All, User.ReadWrite.All, Directory.Read.All, Directory.ReadWrite.All permissions to the managed identity.",
    "3. Authorize Microsoft Entra ID and Office 365 Outlook Logic App connections.",
    "4. For more detailed steps [click Here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Playbooks/Block-AADUser/readme.md)"
  ],
  "lastUpdateTime": "2022-07-11T00:00:00.000Z",
  "entities": [
    "Account"
  ],
  "tags": [
    "Remediation"
  ],
  "support": {
    "tier": "community"
  },
  "author": {
    "name": "John Doe"
  },
  "releaseNotes": [
    {
      "version": "1.0.0",
      "title": "Added manager notification action",
      "notes": [
        "Initial version"
      ]
    }
  ]
}
```

### Parameters Section

#### REQUIRED: PlaybookName Parameter
Every playbook MUST include a `PlaybookName` parameter. This is used for:
- Logic app resource naming
- Connection naming via variables
- Unique deployment identification

**PlaybookName parameter structure:**
```json
"PlaybookName": {
  "defaultValue": "Block-EntraIDUser-Incident",
  "type": "string",
  "metadata": {
    "description": "Name of the playbook resource"
  }
}
```

#### Other Parameters
- Every parameter MUST have:
  - `type` - Parameter type (string, int, bool, array, etc.)
  - `description` - Clear description of what the parameter is for
  - `defaultValue` - Default value (required unless parameter is mandatory at deployment)
  - `metadata` - Object containing at least `description` field

### Variables Section
- Use for connection names: `"[concat('connectorname-', parameters('PlaybookName'))]"`
- Examples:
  - `AzureADConnectionName`
  - `MicrosoftSentinelConnectionName`
  - `Office365ConnectionName`
- Avoid hardcoding resource references

### Resources Section - Microsoft.Web/connections

---

## Authentication & Managed Identities

### REQUIRED: Use Managed Service Identity (MSI)

For Azure services (Sentinel, Azure AD, Key Vault, Storage):

**Workflow Identity:**
- Logic app must have `identity.type: "SystemAssigned"`

**Sentinel Connection:**
- Must include in workflow definition parameters:
  ```json
  "connectionProperties": {
    "authentication": {
      "type": "ManagedServiceIdentity"
    }
  }
  ```

**HTTP Actions (Direct API Calls):**
- Inside action `inputs.authentication`:
  ```json
  {
    "type": "ManagedServiceIdentity",
    "audience": "https://graph.microsoft.com/"
  }
  ```

**Security Requirements:**
- Never hardcode secrets or API keys
- Never store credentials in connection customParameterValues
- Use Key Vault references for sensitive values
- Do NOT use user-assigned identities for Azure service connections

---

## Azure Web Connections (Microsoft.Web/connections)

Each `Microsoft.Web/connections` resource must include:
- `type`: `"Microsoft.Web/connections"`
- `apiVersion`: `"2016-06-01"`
- `name`: Must use variable with pattern `[concat('connectorname-', parameters('PlaybookName'))]`
- `location`: `"[resourceGroup().location]"`
- `kind`: `"V1"` (for Microsoft Sentinel connections; omit for others)
- `properties.displayName`: Name for the connection (use variable)
- `properties.api.id`: Connector reference in format:
  ```
  /subscriptions/{subscriptionId}/providers/Microsoft.Web/locations/{location}/managedApis/{connectorName}
  ```
- `properties.customParameterValues`: `{}` (empty object for most connectors)
- `properties.parameterValueType`: `"Alternative"` (for Microsoft Sentinel)

Examples of connector names in API ID:
- `azuread` - Microsoft Entra ID
- `azuresentinel` - Microsoft Sentinel
- `office365` - Office 365 Outlook

---

## Logic App Workflow (Microsoft.Logic/workflows)

### Workflow Resource Structure
Must include:
- `type`: `"Microsoft.Logic/workflows"`
- `apiVersion`: `"2017-07-01"`
- `name`: `"[parameters('PlaybookName')]"`
- `location`: `"[resourceGroup().location]"`
- `tags`: 
  - `"LogicAppsCategory": "security"`
  - `"hidden-SentinelTemplateName": "[playbook-name]"`
  - `"hidden-SentinelTemplateVersion": "[version]"`
- `identity`:
  ```json
  {
    "type": "SystemAssigned"
  }
  ```
- `dependsOn`: Array of all connection resource IDs (use `resourceId()`)
- `properties`:
  - `state`: `"Enabled"`
  - `definition`: Complete workflow definition (schema + logic)
  - `parameters`: `$connections` object with connection references

### Workflow Definition (properties.definition)
- `$schema`: `"https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#"`
- `contentVersion`: `"1.0.0.0"`
- `parameters`: Must contain `$connections` (type: Object)
- `triggers`: Define activation (e.g., `ApiConnectionWebhook` for Sentinel incidents)
- `actions`: Workflow logic, loops, conditions, API calls
- `outputs`: Typically empty object `{}`

### Connections in Workflow Parameters
Within `properties.parameters.$connections.value`, each connection must have:
- `connectionId`: `"[resourceId('Microsoft.Web/connections', variables('ConnectionName'))]"`
- `connectionName`: Must match variable name (e.g., `"[variables('AzureADConnectionName')]"`)
- `id`: Full managedApis path
- `connectionProperties`: For Sentinel:
  ```json
  {
    "authentication": {
      "type": "ManagedServiceIdentity"
    }
  }
  ```

---

## Custom Connector Requirements

### OpenAPI Definition (Swagger)
- Must include OpenAPI specification for the API
- Must document all endpoints, parameters, and responses
- Must include authentication method in definition
- Must validate against OpenAPI standards

### Custom Connector ARM Template
- Must NOT include `runtimeUrls`, `apiDefinitions`, or `wsdlDefinition` fields
- Must include `swagger` content and `backendService` configuration
- Must have valid `host`, `basePath`, and `schemes` parameters
- Must document API parameters and authentication configuration
- Must specify required vs optional parameters

---

## Documentation Requirements

README.md is **MANDATORY** for all playbooks and custom connectors. Must include:

- **Title and Description** - Purpose and use case
- **Prerequisites** - Subscriptions, licenses, permissions, roles, service accounts, API keys
- **Deployment Instructions** - Parameter descriptions, values, configuration steps
- **Post-Deployment Configuration** - Authentication, manual setup, permissions, testing
- **Usage & Triggering** - Manual/automatic trigger details, trigger conditions, examples
- **Troubleshooting** - Common issues, solutions, log locations, connection validation

---

## Naming Conventions

### Playbook Names
- Use action-oriented verbs: `Enrich`, `Block`, `Sync`, `Alert`, `Disable`, `Add`, `Update`
- Format: `[Action]-[Entity/System]` or `[Solution]-[Action]`

### Connection Names
- Format: `[ConnectorType]_Connection`

### Parameter Names
- Use PascalCase
- Be descriptive and meaningful

### Resource Names
- Use consistent prefix for related resources

---

## Code Quality Standards

### Error Handling
- All external API calls must have error handling
- Use try-catch patterns or error action configurations
- Errors must log appropriately with meaningful messages

### Input Validation
- All input parameters must be validated for type and format
- Check for empty or null values
- Implement bounds checking for numeric parameters
- Sanitize inputs if used in external API calls

### Performance Considerations
- Minimize nested loops and API calls
- Consider throttling limits of called services
- Implement timeouts for external API calls

### Logging & Monitoring
- Implement appropriate logging for audit trails
- Use Logic Apps diagnostic logging and run history
- Document monitoring and troubleshooting procedures

---

## PR Review Validation

When reviewing playbooks in pull requests, validate against these criteria:

### File Structure Check
- ✓ `azuredeploy.json` exists in correct directory
- ✓ `README.md` exists and is complete (all 6 sections required)
- ✓ No unnecessary or temporary files

### ARM Template Root Validation
- ✓ `$schema` is `"https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"`
- ✓ `contentVersion` follows format `"1.0.0.0"` or similar
- ✓ Top-level sections present: metadata, parameters, variables, resources
- ✓ Valid JSON syntax

### Metadata Section Validation
- ✓ `title` - Present and descriptive
- ✓ `description` - Present and clear
- ✓ `author.name` - Present (not just string)
- ✓ `support.tier` - One of: "community", "partner", "microsoft"
- ✓ `prerequisites` - Array of strings explaining requirements
- ✓ `postDeployment` - Array of numbered steps for setup
- ✓ `lastUpdateTime` - Valid ISO 8601 timestamp format
- ✓ `entities` - Array with supported entity types (Account, IP, URL, etc.)
- ✓ `tags` - Array with action tags (Remediation, Response, etc.)
- ✓ `releaseNotes` - Array with version objects containing `version`, `title`, `notes`

### Parameters Validation
- ✓ **PlaybookName parameter EXISTS** (REQUIRED - mandatory for all playbooks)
- ✓ PlaybookName has `type: "string"`
- ✓ PlaybookName has `defaultValue` defined (e.g., "Block-EntraIDUser-Incident")
- ✓ PlaybookName has descriptive `description` in metadata
- ✓ All other parameters have `type` property
- ✓ All other parameters have descriptive `description`
- ✓ All parameters have `defaultValue` (or appropriately omitted if required)

### Variables Validation
- ✓ Connection names use pattern: `[concat('name-', parameters('PlaybookName'))]`
- ✓ No hardcoded subscription IDs, tenant IDs, or resource names
- ✓ All variables referenced in resources section

### Resources - Connections Validation
- ✓ Each connection resource has:
  - `type`: `"Microsoft.Web/connections"`
  - `apiVersion`: `"2016-06-01"`
  - `name`: Uses variable, NOT hardcoded
  - `location`: Uses `[resourceGroup().location]`
  - `kind`: `"V1"` for Sentinel; omit for others
  - `properties.displayName`: Uses variable
  - `properties.api.id`: Full path format with `subscriptions()` function
  - `properties.customParameterValues`: `{}`
- ✓ No missing or misspelled connector names

### Resources - Logic App Workflow Validation
- ✓ Resource has:
  - `type`: `"Microsoft.Logic/workflows"`
  - `apiVersion`: `"2017-07-01"`
  - `name`: `"[parameters('PlaybookName')]"` (NOT hardcoded)
  - `location`: `"[resourceGroup().location]"`
  - `identity.type`: `"SystemAssigned"`
  - `tags` with `LogicAppsCategory: "security"`, sentinel metadata tags
  - `dependsOn`: Array of all connection `resourceId()` calls
  - `properties.state`: `"Enabled"`

### Workflow Definition Validation
- ✓ Definition `$schema` is correct Logic Apps schema
- ✓ `contentVersion` present
- ✓ `parameters.$connections` declared as Object type
- ✓ `triggers` section includes appropriate trigger (e.g., Sentinel incident)
- ✓ `actions` section present with valid logic
- ✓ All actions reference connections via `parameters('$connections')`

### Connections Parameters in Workflow
- ✓ Each connection in `$connections.value` has:
  - `connectionId`: Proper `resourceId()` reference
  - `connectionName`: Matches variable name from variables section
  - `id`: Full managedApis path for connector
  - For Sentinel: `connectionProperties.authentication.type == "ManagedServiceIdentity"`

### Security Review
- ✓ No hardcoded credentials, API keys, or secrets
- ✓ No hardcoded subscription IDs, tenant IDs, or object IDs
- ✓ No user passwords or personal information
- ✓ Sensitive values use Key Vault references if needed
- ✓ Sentinel connections use MSI authentication
- ✓ HTTP actions calling Microsoft Graph use MSI with proper audience

### Custom Connector Review (if applicable)
- ✓ OpenAPI/Swagger definition is present and valid
- ✓ API endpoints documented with parameters and responses
- ✓ Authentication method specified in connector
- ✓ Custom connector ARM template removes `runtimeUrls`, `apiDefinitions`, `wsdlDefinition`
- ✓ `swagger` and `backendService` configuration included
- ✓ `host`, `basePath`, `schemes` are valid

### Documentation Review
- ✓ README.md includes all 6 required sections
- ✓ Title and description accurately reflect functionality
- ✓ Prerequisites section lists all required roles, permissions, API access
- ✓ Deployment section explains each parameter
- ✓ Post-deployment section includes specific configuration steps
- ✓ Usage section explains triggering and expected behavior
- ✓ Troubleshooting section addresses common issues

---