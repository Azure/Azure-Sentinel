# Silent Push Logic Apps custom connector

This custom connector (`SilentPush-API`) connects Azure Logic Apps to the [Silent Push](https://www.silentpush.com) public API. It exposes nearly all Silent Push API endpoints (enrichment, passive DNS explore and search, exports, feeds, live scan, SPQL and threat check), so you can build your own playbooks from scratch.

All Silent Push playbooks in this solution use this connector, so **deploy it first**.

### Authentication

API key. You are asked for your Silent Push API key when you create a connection. Sign up at https://app.silentpush.com to get one.

### Deployment instructions

1. Click **Deploy to Azure**. This opens the ARM template deployment wizard.
2. Pick the subscription and the resource group where your playbooks will live (the same resource group as the playbooks).
3. Fill in the parameters:
    * **CustomConnectorName**: name of the connector (default `SilentPush-API`). If you change it, use the same value for `CustomConnectorName` when deploying the playbooks.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSilentPush%2FConnector%2FSilentPushCustomConnector%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSilentPush%2FConnector%2FSilentPushCustomConnector%2Fazuredeploy.json)
