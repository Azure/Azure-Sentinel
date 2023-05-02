# Deploy widgets

To deploy widgets to a workspace:

## Create a Key Vault to store widgets credentials

Download the [CreateKV](https://aka.ms/SentinelWidgetsDeployScript) python script. and then execute it using the following command:

``` Command Line
python CreateKV.py --subscription-id <subscription id> --resource-group-name <resource group name> --workspace-id <workspace id>
```

Make sure you record the Key Vault name that the script prints as you will need it to configure the widgets. If you did not recorc the name, us the following command to get it without recreating the Key Vault:

``` Command Line
python CreateKV.py --subscription-id <subscription id> --resource-group-name <resource group name> --workspace-id <workspace id> --print_kv_name True
```

## Configure widgets

For each widget, configure the secrets and other parameters it reqruies using the links below, which will help you to store them in the workspace Key Vault.

- [Configure Anomaly](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fwidgets%2FWidgets%2FDeployment%2FAddAnomaliConnection.json)
