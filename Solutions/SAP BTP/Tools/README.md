# SAP BTP Integration Tools

This directory contains PowerShell script blue prints to handle Microsoft Sentinel Solution for SAP BTP onboarding with SAP Business Technology Platform subaccounts using the CloudFoundry environment at scale.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Choose Your Deployment Model](#choose-your-deployment-model)
- [Split Persona](#split-persona)
  - [Initial Deployment](#split-persona-initial-deployment)
  - [Key Rotation](#split-persona-key-rotation)
- [Single Persona](#single-persona)
  - [Initial Deployment](#single-persona-initial-deployment)
  - [Key Rotation](#single-persona-key-rotation)
- [Key Rotation Modes](#key-rotation-modes)

## Scripts

- `provision-audit-to-subaccount.ps1`: Script to provision auditlog management service in SAP BTP subaccounts. It reads subaccount details from a CSV file and provisions the service using the CloudFoundry CLI.
- `connect-sentinel-to-btp.ps1`: Main script to connect Microsoft Sentinel Solution for SAP BTP to SAP BTP subaccounts. It reads subaccount details from a CSV file, reads the SAP BTP service keys, and creates connections in the Sentinel SAP BTP data connector.
- `export-subaccounts.ps1`: Script to enumerate SAP BTP subaccounts and export them to a CSV file for use with other scripts.
- `BtpHelpers.ps1`: Helper functions used by the main scripts for tasks such as logging, authentication, and API interactions.

## Prerequisites

Ensure you have the following:
- PowerShell 7 or later
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and authenticated
- [CloudFoundry CLI](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html) installed and authenticated
- Appropriate permissions in both Azure and SAP BTP. Learn more [here](https://learn.microsoft.com/azure/sentinel/sap/deploy-sap-btp-solution#prerequisites)

## Choose Your Deployment Model

**Split Persona:** Separate SAP BTP and Microsoft Sentinel administrators without cross-access. BTP admins provision services and export credentials to Azure Key Vault. Sentinel admins retrieve credentials from Key Vault to create connections. This approach maintains security boundaries and enables zero-downtime key rotation.

**Single Persona:** One administrator with access to both SAP BTP and Microsoft Sentinel. Simpler workflow but requires broader permissions.

---

## Split Persona

### Initial Deployment

**Step 1: SAP BTP Admin - Generate subaccounts CSV**

```powershell
.\export-subaccounts.ps1 -BtpSubdomain "<global-account-subdomain>"

# (Or manually create the CSV file using subaccounts-sample.csv as template)
```

**Step 2: SAP BTP Admin - Provision audit services and export credentials**

```powershell
# Export to Key Vault (recommended)
.\provision-audit-to-subaccount.ps1 -ExportCredentialsToKeyVault -KeyVaultName "<kv-name>"

# Export to CSV (not recommended)
# .\provision-audit-to-subaccount.ps1 -ExportCredentialsToCsv
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

## Single Persona

### Initial Deployment

**Step 1: Generate subaccounts CSV**

```powershell
.\export-subaccounts.ps1 -BtpSubdomain "<global-account-subdomain>"

# (Or manually create the CSV file using subaccounts-sample.csv as template)
```

**Step 2: Provision audit services**

```powershell
.\provision-audit-to-subaccount.ps1
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

## Key Rotation Modes

- **CreateNewKey** (default): Creates new key, keeps old keys → zero downtime
- **Cleanup**: Keeps newest key, deletes old keys → run after rotation confirmed

## Contributing

This project welcomes contributions and suggestions. See the [Contributing section](https://github.com/Azure/Azure-Sentinel?tab=readme-ov-file#contribution-guidelines) of this repos for reference.
