# SAP BTP Integration Tools

This directory contains PowerShell script blue prints to handle Microsoft Sentinel Solution for SAP BTP onboarding with SAP Business Technology Platform subaccounts using the CloudFoundry environment at scale.

## Scripts

- `provision-audit-to-subaccount.ps1`: Script to provision auditlog management service in SAP BTP subaccounts. It reads subaccount details from a CSV file and provisions the service using the CloudFoundry CLI.
- `connect-sentinel-to-btp.ps1`: Main script to connect Microsoft Sentinel Solution for SAP BTP to SAP BTP subaccounts. It reads subaccount details from a CSV file, reads the SAP BTP service keys, and creates connections in the Sentinel SAP BTP data connector.
- `export-subaccounts.ps1`: Script to enumerate SAP BTP subaccounts and export them to a CSV file for use with other scripts.
- `BtpHelpers.ps1`: Helper functions used by the main scripts for tasks such as logging, authentication, and API interactions.

## Getting Started

1. Ensure you have the prerequisites:
   - PowerShell 7 or later
   - [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and authenticated
   - [CloudFoundry CLI](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html) installed and authenticated
   - Appropriate permissions in both Azure and SAP BTP. Learn more [here](https://learn.microsoft.com/azure/sentinel/sap/deploy-sap-btp-solution#prerequisites)
   - (Optionally) install the SAP BTP CLI for subaccount enumeration and CSV file generation. Learn more [here](https://help.sap.com/docs/BTP/5f2f6f2f1e2b4f3ea5e8f3d6c4c5e6b7/cli-installation).
2. Use the [subaccounts-sample.csv](subaccounts-sample.csv) file to create your own `subaccounts.csv` file with your SAP BTP subaccount details or use the `export-subaccounts.ps1` script to generate it automatically.
3. Run the scripts in the following order:

   - (Optionally) run `export-subaccounts.ps1` to generate the CSV file with your SAP BTP subaccount details. Sample commands to fetch global account info and trigger the onboarding info export:

    ```powershell
    btp get accounts/global-account
    ```

    Use the retrieved global account subdomain (e.g. "my-global-account-12345") to run:

     ```powershell
     $securePassword = Read-Host "Enter BTP Password" -AsSecureString
     .\export-subaccounts.ps1 -CfUsername "<btp-username>" -CfPassword -BtpSubdomain "<btp-global-account>-<id>"
     ```

   - First, run `provision-audit-to-subaccount.ps1` to provision the auditlog service. Sample command:

     ```powershell
     $securePassword = Read-Host "Enter CF Password" -AsSecureString
     .\provision-audit-to-subaccount.ps1 -CfUsername "<cf-username>" -CfPassword $securePassword
     ```

   - Then, run `connect-sentinel-to-btp.ps1` to create connections in the Sentinel SAP BTP data connector. Sample command:

     ```powershell
     $securePassword = Read-Host "Enter CF Password" -AsSecureString
     .\connect-sentinel-to-btp.ps1 -SubscriptionId "<azure-sentinel-sub-id>" -ResourceGroupName "<rg-name-sentinel-workspace>" -WorkspaceName "<sentinel-workspace-name>" -CfUsername "<cf-username>" -CfPassword $securePassword
     ```

## Lifecycle Management

It is recommend to rotate service keys for security best practices. Consider Azure Key Vault integration for managing secrets. Expiry events can be acted upon from Azure Logic Apps or Azure Functions to trigger the rotation process. See "[Rotate the BTP client secret](https://learn.microsoft.com/azure/sentinel/sap/deploy-sap-btp-solution#rotate-the-btp-client-secret)" section on Microsoft Learn for more details.

## Contributing

This project welcomes contributions and suggestions. See the [Contributing section](https://github.com/Azure/Azure-Sentinel?tab=readme-ov-file#contribution-guidelines) of this repos for reference.
