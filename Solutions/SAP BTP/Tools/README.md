# SAP BTP Integration Tools

This directory contains PowerShell script blue prints to handle Microsoft Sentinel Solution for SAP BTP onboarding with SAP Business Technology Platform subaccounts using the CloudFoundry environment at scale.

## Table of Contents

- [Scripts](#scripts)
- [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Examples](#examples)
  - [Split Permissions](#split-permissions)
  - [Full Permissions](#full-permissions)

## Scripts

- `provision-audit-to-subaccounts.ps1`: Script to provision auditlog management service in SAP BTP subaccounts. It reads subaccount details from a CSV file and provisions the service using the CloudFoundry CLI.
- `connect-sentinel-to-btp.ps1`: Main script to connect Microsoft Sentinel Solution for SAP BTP to SAP BTP subaccounts. It reads subaccount details from a CSV file, reads the SAP BTP service keys, and creates connections in the Sentinel SAP BTP data connector.
- `export-subaccounts.ps1`: Script to enumerate SAP BTP subaccounts and export them to a CSV file for use with other scripts.
- `BtpHelpers.ps1`: Helper functions used by the main scripts for tasks such as logging, authentication, and API interactions.

## Prerequisites

Ensure you have the following:
- PowerShell 7 or later
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and authenticated
- [BTP CLI](https://help.sap.com/docs/btp/sap-business-technology-platform/download-and-start-using-btp-cli-client) installed and in path
- [CloudFoundry CLI](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html) installed and authenticated
- Appropriate permissions in both Azure and SAP BTP. Learn more [here](https://learn.microsoft.com/azure/sentinel/sap/deploy-sap-btp-solution#prerequisites)
- Azure Key Vault (optional, required for split permissions workflow)

## Usage

### export-subaccounts.ps1

Generates a CSV file with all subaccounts from your BTP global account.

**Parameters:**
- `-BtpSubdomain`: Your BTP global account subdomain

### provision-audit-to-subaccounts.ps1

Provisions auditlog management services and creates service keys.

**Parameters:**
- `-CsvPath`: Path to subaccounts CSV file (default: `.\subaccounts.csv`)
- `-InstanceName`: Service instance name (default: `sentinel-audit-srv`)
- `-KeyRotationMode`: Key rotation mode
  - `CreateNewKey` (default): Creates new key, keeps old keys → zero downtime
  - `Cleanup`: Keeps newest key, deletes old keys → run after rotation confirmed
- `-ExportCredentialsToKeyVault`: Export credentials to Azure Key Vault (recommended for split permissions)
- `-KeyVaultName`: Key Vault name (required with `-ExportCredentialsToKeyVault`)
- `-ExportCredentialsToCsv`: Export credentials to CSV (not recommended)

### connect-sentinel-to-btp.ps1

Creates or updates Sentinel connections to BTP subaccounts.

**Parameters:**
- `-SubscriptionId`: Azure subscription ID
- `-ResourceGroupName`: Resource group containing Sentinel workspace
- `-WorkspaceName`: Sentinel workspace name
- `-CsvPath`: Path to subaccounts CSV file (default: `.\subaccounts.csv`)
- `-UseKeyVault`: Retrieve credentials from Key Vault (for split permissions)
- `-KeyVaultName`: Key Vault name (required with `-UseKeyVault`)
- `-UseCredentialsFromCsv`: Retrieve credentials from CSV (not recommended)

## Examples

## Split Permissions

**Use this if your permissions are separated:** You have separate SAP BTP and Microsoft Sentinel administrators without cross-access. BTP admins cannot access Sentinel, and Sentinel admins cannot access BTP.

**How it works:** BTP admins provision services and export credentials to a central Azure Key Vault. Sentinel admins retrieve credentials from Key Vault to create connections. This approach maintains security boundaries and enables zero-downtime key rotation.

**Required permissions:**
- BTP Admins: `Key Vault Secrets Officer` role to upload service keys
- Sentinel Admins: `Key Vault Secrets User` role to read secrets

**Security Note:** CSV export is supported for testing but not recommended for production. CSV files store credentials in plaintext without encryption, access controls, or audit trails. Use Azure Key Vault for production deployments to maintain proper security boundaries.

### Initial Deployment

**Step 1: SAP BTP Admin - Generate subaccounts CSV**

```powershell
.\export-subaccounts.ps1 -BtpSubdomain "<global-account-subdomain>"

# (Or manually create the CSV file using subaccounts-sample.csv as template)
```

**Step 2: SAP BTP Admin - Provision audit services and export credentials**

```powershell
# Export to Key Vault (recommended)
.\provision-audit-to-subaccounts.ps1 -ExportCredentialsToKeyVault -KeyVaultName "<kv-name>"

# Export to CSV (not recommended)
# .\provision-audit-to-subaccounts.ps1 -ExportCredentialsToCsv
```

**Step 3: Sentinel Admin - Create Sentinel connections**

```powershell
# From Key Vault
.\connect-sentinel-to-btp.ps1 -SubscriptionId "<sub-id>" -ResourceGroupName "<rg>" -WorkspaceName "<ws>" -UseKeyVault -KeyVaultName "<kv-name>"

# From CSV (if using CSV export)
# .\connect-sentinel-to-btp.ps1 -SubscriptionId "<sub-id>" -ResourceGroupName "<rg>" -WorkspaceName "<ws>" -UseCredentialsFromCsv
```

### Key Rotation

It is recommend to rotate service keys for security best practices. Zero-downtime rotation is supported through Key Vault secret versioning. See "[Rotate the BTP client secret](https://learn.microsoft.com/azure/sentinel/sap/deploy-sap-btp-solution#rotate-the-btp-client-secret)" section on Microsoft Learn for more details.

**Step 1: SAP BTP Admin - Create new keys**

```powershell
# Export to Key Vault (recommended)
.\provision-audit-to-subaccounts.ps1 -KeyRotationMode CreateNewKey -ExportCredentialsToKeyVault -KeyVaultName "<kv-name>"

# Export to CSV (not recommended)
# .\provision-audit-to-subaccounts.ps1 -KeyRotationMode CreateNewKey -ExportCredentialsToCsv
```

**Step 2: Sentinel Admin - Update connections**

```powershell
# From Key Vault
.\connect-sentinel-to-btp.ps1 -SubscriptionId "<sub-id>" -ResourceGroupName "<rg>" -WorkspaceName "<ws>" -UseKeyVault -KeyVaultName "<kv-name>"

# From CSV (if using CSV export)
# .\connect-sentinel-to-btp.ps1 -SubscriptionId "<sub-id>" -ResourceGroupName "<rg>" -WorkspaceName "<ws>" -UseCredentialsFromCsv
```

**Step 3: SAP BTP Admin - Clean up old keys**

```powershell
.\provision-audit-to-subaccounts.ps1 -KeyRotationMode Cleanup
```

---

## Full Permissions

**Use this if you have access to both Sentinel and BTP:** You have a single administrator (or team) with access to both SAP BTP and Microsoft Sentinel.

**How it works:** Simpler workflow where the same person runs both provisioning and connection scripts directly without credential handoff via Key Vault.

### Initial Deployment

**Step 1: Generate subaccounts CSV**

```powershell
.\export-subaccounts.ps1 -BtpSubdomain "<global-account-subdomain>"

# (Or manually create the CSV file using subaccounts-sample.csv as template)
```

**Step 2: Provision audit services**

```powershell
.\provision-audit-to-subaccounts.ps1
```

**Step 3: Create Sentinel connections**

```powershell
.\connect-sentinel-to-btp.ps1 -SubscriptionId "<sub-id>" -ResourceGroupName "<rg>" -WorkspaceName "<ws>"
```

### Key Rotation

It is recommend to rotate service keys for security best practices. See "[Rotate the BTP client secret](https://learn.microsoft.com/azure/sentinel/sap/deploy-sap-btp-solution#rotate-the-btp-client-secret)" section on Microsoft Learn for more details.

**Zero-downtime rotation:**

```powershell
# Step 1: Create new keys
.\provision-audit-to-subaccounts.ps1 -KeyRotationMode CreateNewKey

# Step 2: Update connections
.\connect-sentinel-to-btp.ps1 -SubscriptionId "<sub-id>" -ResourceGroupName "<rg>" -WorkspaceName "<ws>"

# Step 3: Clean up old keys
.\provision-audit-to-subaccounts.ps1 -KeyRotationMode Cleanup
```

---

## Contributing

This project welcomes contributions and suggestions. See the [Contributing section](https://github.com/Azure/Azure-Sentinel?tab=readme-ov-file#contribution-guidelines) of this repos for reference.
