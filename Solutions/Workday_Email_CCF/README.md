# Workday Email ID Change Connector

This module deploys the Workday Email ID Change data connector to Microsoft Sentinel. It ingests Email ID Change reports from the Workday Custom Report API into the `ASimAuditEventLogs` table using the ASIM Audit Event schema.

## What This Module Does

This Terraform module provisions the Workday Email ID Change data connector for Microsoft Sentinel with the following capabilities:

1. **Deploys the Workday Email Solution** — Registers the content package, connector definition, and connection templates in Microsoft Sentinel via `PollerConnector.json`
2. **Creates Data Collection Resources** — Provisions a Data Collection Endpoint (DCE) and Data Collection Rule (DCR) with KQL transformation to map Workday Email ID Change fields to the ASIM Audit Event schema
3. **Deploys Connector Pollers** — Creates RestApiPoller data connectors that poll the Workday Custom Report API using OAuth 2.0 authorization code flow
4. **Fetches Secrets from Key Vault** — Securely retrieves Client ID and Client Secret from an existing Azure Key Vault
5. **Supports Multiple Environments** — Separate configurations for poc, dev, nonprod, and prod

## Architecture

```
Key Vault (existing)
  ├── workday-email-client-id
  └── workday-email-client-secret
          │
          ▼
Terraform (main.tf)
  ├── ARM Deployment: PollerConnector.json (Solution + Connector Definition)
  ├── DCE: Data Collection Endpoint
  ├── DCR: Data Collection Rule (KQL transform → ASimAuditEventLogs)
  └── ARM Deployment: connection-template.json (RestApiPoller)
          │
          ▼
Workday Custom Report API (CR_Sentinel_Email_ID_Change)  →  Microsoft Sentinel (ASimAuditEventLogs)
```

## Data Mapping (KQL Transform)

| Workday Field | ASIM Field | Description |
|---|---|---|
| `DateTimeStamp` | `TimeGenerated`, `EventStartTime`, `EventEndTime` | Timestamp of the email change event |
| `EmailIDBefore` | `OldValue` | Previous email address |
| `EmailIDAfter` | `NewValue` | New email address |
| `Employee_ID` | `ActorUserId` | Employee identifier |
| `Login_ID` | `ActorUsername` | Login identifier |
| `TargetID` | `EventOriginalUid` | Workday target object ID |
| `Worker` | `Object` | Worker name whose email was changed |

Static enrichments: `EventType=Set`, `Operation=Email ID Change`, `EventProduct=Workday`, `EventVendor=Workday`, `EventSchema=AuditEvent`, `EventSchemaVersion=0.1`

## Directory Structure

```
connectors/workday-email/
├── main.tf                           # Resource definitions (solution, DCE, DCR, connectors)
├── variables.tf                      # Variable definitions with validations
├── locals.tf                         # Local values (naming, computed resource names)
├── data.tf                           # Data sources (resource group, workspace, Key Vault, secrets)
├── outputs.tf                        # Output definitions
├── providers.tf                      # Provider configuration
├── versions.tf                       # Terraform and provider version constraints
├── PollerConnector.json              # ARM template for Workday Email solution deployment
├── connection-template.json          # ARM template for RestApiPoller data connectors
├── DataConnectionRules.json          # Data connection rules definition
├── DataConnectorDefination.json      # Data connector definition
├── PollingConfig.json                # Polling configuration
├── description.json                  # Connector description metadata
├── README.md                         # This file
└── environment/                      # Environment-specific configurations
    ├── poc-north-europe.tfvars       # POC environment variables
    ├── dev-north-europe.tfvars       # Development environment variables
    ├── nonprod-north-europe.tfvars   # Non-production environment variables
    ├── prod-north-europe.tfvars      # Production environment variables
    ├── config.poc.tfbackend          # POC backend configuration
    ├── config.dev.tfbackend          # Dev backend configuration
    ├── config.nonprod.tfbackend      # Non-prod backend configuration
    └── config.prod.tfbackend         # Production backend configuration
```

## Prerequisites

- Terraform >= 1.3.0
- Azure CLI installed and authenticated
- Existing Microsoft Sentinel workspace
- Azure Key Vault with Workday Email API credentials stored as secrets
- Required RBAC permissions:
  - **Key Vault Secrets User** — On the Key Vault containing Workday credentials
  - **Contributor** — On the resource group containing Microsoft Sentinel
  - **Storage Blob Data Contributor** — On the storage account for Terraform state
