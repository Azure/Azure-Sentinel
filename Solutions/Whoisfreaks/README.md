# WhoisFreaks for Microsoft Sentinel

Microsoft Sentinel Content Hub solution that ingests WhoisFreaks threat intelligence and newly registered domain feeds via an Azure Function and the Azure Monitor Logs Ingestion API.

## End-user experience

This solution installs in two steps:

1. **Install from Content Hub** (`Package/mainTemplate.json`). This registers the WhoisFreaks data connector UI and solution metadata in your Sentinel workspace. It does **not** create any Azure infrastructure.
2. **Deploy the infrastructure** (`Package/azuredeploy.json`), via the **Deploy to Azure** button in the connector's instructions or `az deployment group create`. This is where you provide:
   - your WhoisFreaks **API key** (stored as a secure Function App setting, never in source control), and
   - which **feeds** to enable (malware, phishing, spam, NRD variants).

After deployment, the Data connectors page shows connection status. Feeds can be changed later via the Function App's application settings (`WHOISFREAKS_FEED_*_ENABLED`) without redeploying.

## Included

- `Package/mainTemplate.json` -- Content Hub package (connector UI + solution metadata only).
- `Package/azuredeploy.json` -- infrastructure template:
  - Azure Function App (Python, Linux Consumption plan) with a system-assigned managed identity
  - A storage account for checkpointing and distributed feed locks
  - A Data Collection Endpoint and Data Collection Rule, with one stream declaration per feed
  - The 7 custom Log Analytics tables the feeds ingest into, with schemas generated directly from the Function's own normalizer output
  - Role assignments granting the Function's identity `Storage Blob Data Contributor` (storage account) and `Monitoring Metrics Publisher` (DCR)
- `Package/FunctionApp.zip` -- the packaged Function code that `azuredeploy.json` deploys via `WEBSITE_RUN_FROM_PACKAGE`.
- `Package/createUiDefinition.json` -- Content Hub install experience (workspace selection only).

## Supported feeds

- Malware, Phishing, Spam
- NRD gTLD / ccTLD with WHOIS
- NRD gTLD / ccTLD without WHOIS

## Schedule

Daily at **00:00 UTC** (timer trigger). Manual trigger: Function `/api/run`.

## Package URL

After merge into [Azure/Azure-Sentinel](https://github.com/Azure/Azure-Sentinel), `azuredeploy.json`'s default `functionPackageUrl` parameter resolves to:

```text
https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Whoisfreaks/Package/FunctionApp.zip
```

`Package/FunctionApp.zip` is committed in this solution folder for that path to resolve. Before merge, see `DEPLOYMENT_AND_TESTING.md` section 3.2 for hosting it yourself.

## Validation before PR

1. Run the Microsoft Sentinel solution packaging tooling: `Tools/Create-Azure-Sentinel-Solution/V3`.
2. ARM-validate both `Package/mainTemplate.json` and `Package/azuredeploy.json` (arm-ttk).
3. Deploy `azuredeploy.json` into a test workspace and confirm at least one enabled feed ingests into the corresponding `*_CL` table (see `DEPLOYMENT_AND_TESTING.md`).
4. Run the Python unit tests: `cd FunctionApp && PYTHONPATH=. python -m pytest tests/ -v`.

## Security

- The WhoisFreaks API key is a `securestring` parameter of `azuredeploy.json`, collected only from the customer when they deploy the infrastructure -- never committed to source control.
- Function App uses a system-assigned managed identity for both storage (checkpoints/locks) and DCR ingestion; no connection strings or keys are stored in the Function's own code.
