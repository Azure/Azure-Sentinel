# Send Incident to Cyware Orchestrate

This Azure Logic App template is designed to integrate Azure Sentinel incidents with Cyware Orchestrate, enabling automated incident response actions. When an Azure Sentinel alert triggers, this Logic App automatically sends the incident details to Cyware Orchestrate.

## Prerequisites

Before deploying this template, you should have:

1. An Azure account with active subscriptions.
2. Azure Sentinel setup in your Azure environment.
3. Access to Cyware Orchestrate and a configured Webhook URL for incident intake.

## Deployment Guide

This guide provides instructions on manually deploying the Logic App using Azure Portal and via Azure CLI.

### Azure Portal

1. **Download Templates:** Download the `azuredeploy.json` and `azuredeploy.parameters.json` files from this repository.
2. **Open Azure Portal:** Log in to your Azure Portal.
3. **Create a Resource:** Go to "Create a resource" > "Template deployment (deploy using custom templates)".
4. **Load the Template:** Upload or paste the content of `azuredeploy.json` file.
5. **Customize Parameters:** Fill in the parameters accordingly. The `azuredeploy.parameters.json` file can help provide the structure required.
6. **Review + create:** After validating the template and parameters, proceed to create the Logic App.

### Azure CLI

To deploy using Azure CLI, ensure you have Azure CLI installed and configured. Then run the following command:

```bash
az deployment group create --resource-group <YourResourceGroupName> --template-file ./azuredeploy.json --parameters @azuredeploy.parameters.json
```

Replace `<YourResourceGroupName>` with the name of your Azure resource group.

## Configuration

After deployment, ensure to configure the following parameters appropriately:

- `LogicAppLocation`: The location of your Logic App instance.
- `COWebHookURL`: The Webhook URL provided by Cyware Orchestrate for incident intake.
- `connections_azuresentinel_connectionId`: The connection string for Azure Sentinel. This requires creating a connection resource in your Azure environment.

Refer to the `azuredeploy.parameters.json` as an example. Ensure to replace the placeholders with actual values relevant to your setup.

## Usage

Once deployed and configured, the Logic App listens for Azure Sentinel alerts based on the triggers defined in the `azuredeploy.json`. When an alert triggers, it automatically sends the incident details to the specified Cyware Orchestrate Webhook URL for further action.

## Customization

You can customize the Logic App workflow by editing the `azuredeploy.json` definition, tailoring actions, and triggers to specific needs.

## Troubleshooting

- Ensure all connections are authenticated and accessible by the Logic App.
- Verify that the Webhook URL from Cyware Orchestrate is correct and accepting requests.

## Contributing

If you have suggestions or improvements, feel free to fork this repository and submit a pull request!

## License

License to go here

## Contact

For help or additional information, contact the repository maintainer at support@cyware.com or submit an issue in this repository.