# SAP BTP Integration Tools

This directory contains PowerShell script blue prints to handle Microsoft Sentinel Solution for SAP BTP onboarding with SAP Business Technology Platform subaccounts using the CloudFoundry environment at scale.

## Scripts

- `provision-audit-to-subaccount.ps1`: Script to provision auditlog management service in SAP BTP subaccounts. It reads subaccount details from a CSV file and provisions the service using the CloudFoundry CLI.
- `connect-sentinel-to-btp.ps1`: Main script to connect Microsoft Sentinel Solution for SAP BTP to SAP BTP subaccounts. It reads subaccount details from a CSV file, reads the SAP BTP service keys, and creates connections in the Sentinel SAP BTP data connector.
- `BtpHelpers.ps1`: Helper functions used by the main script for tasks such as logging, authentication, and API interactions.

## Getting Started

1. Ensure you have the prerequisites:
   - PowerShell 7 or later
   - [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and authenticated
   - [CloudFoundry CLI](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html) installed and authenticated
   - Appropriate permissions in both Azure and SAP BTP. Learn more [here](https://learn.microsoft.com/azure/sentinel/sap/deploy-sap-btp-solution#prerequisites)
2. Use the [subaccounts-sample.csv](subaccounts-sample.csv) file to create your own `subaccounts.csv` file with your SAP BTP subaccount details.
3. Run the scripts in the following order:
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

## Contributing

This project welcomes contributions and suggestions. See the [Contributing section](https://github.com/Azure/Azure-Sentinel?tab=readme-ov-file#contribution-guidelines) of this repos for reference.
