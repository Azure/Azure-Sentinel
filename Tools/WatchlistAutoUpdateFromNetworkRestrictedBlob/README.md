# Watchlist from Storage Azure Function

This Azure Function reads a CSV file from Azure Blob Storage and updates a Microsoft Sentinel Watchlist on a schedule.

## Features
- Timer-triggered Azure Function (runs daily at 2:00 AM UTC)
- Reads a CSV file from Azure Blob Storage using Managed Identities
- Updates a Microsoft Sentinel Watchlist with the file contents or alternatively upload data to a custom table
- Supports batching for large files

## Prerequisites
- Python 3.8+
- Azure Subscription
- Microsoft Sentinel enabled in your Log Analytics workspace
- Required Azure roles:
  - **Storage Blob Data Reader** on the storage account
  - **Microsoft Sentinel Contributor** on the Log Analytics workspace

## Environment Variables
Set these in your `local.settings.json` for local development or as Application Settings in Azure:

| Name                   | Description                                 |
|------------------------|---------------------------------------------|
| WATCHLIST_NAME         | Name of the Sentinel watchlist              |
| AZURE_SUBSCRIPTION_ID  | Azure subscription ID                       |
| RESOURCE_GROUP_NAME    | Resource group containing the workspace     |
| WORKSPACE_NAME         | Log Analytics workspace name                |
| FILE_NAME              | Name of the CSV file in Blob Storage        |
| STORAGE_ACCOUNT_NAME   | Name of the storage account                 |
| STORAGE_CONTAINER_NAME | Name of the blob container                  |
| WATCHLIST_PROVIDER     | Provider name for the watchlist             |
| WATCHLIST_SEARCH_KEY   | Search key for the watchlist                |
| WATCHLIST_DESCRIPTION  | Description of the watchlist                |

## Local Development
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Start Azurite (for local blob storage emulation) or use a real Azure Storage account.
3. Update `local.settings.json` with your environment variables.
4. Run the function locally:
   ```sh
   func start
   ```

## Deployment
Deploy to Azure using the Azure Functions extension for VS Code or Azure CLI.

## Notes
- The function uses `DefaultAzureCredential` for authentication. Ensure your environment is authenticated (e.g., `az login`).
- For large files, the function batches updates to avoid API limits.

## License
MIT License
