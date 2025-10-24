# Cyera → Sentinel: ARM/Bicep deployment (DCE, DCR, LA tables, Function, RBAC)

## Structure
- `infra/main.bicep` – entry point
- `infra/modules/*` – DCE, DCR (with transforms), LA tables (deployment script), Storage, Function, RBAC
- `infra/parameters/main.sample.bicepparam` – sample param file
- `artifacts/transforms/*.kql` – KQL transforms (assets_ms, assets_ext)
- `artifacts/tables/*.json` – table schemas
- `scripts/upload_function_package.sh` – helper to host the function zip via SAS and set run-from-package

## Prereqs
- Azure CLI >= 2.53 (tables script uses 2.63.0)
- Resource group + Log Analytics workspace exist
- Function package zip (public URL or use helper to generate SAS)

## Deploy
```bash
az deployment group what-if -g <rg> -f infra/main.bicep -p @infra/parameters/main.sample.bicepparam
az deployment group create -g <rg> -f infra/main.bicep -p @infra/parameters/main.sample.bicepparam
```

If you did not set `functionPackageUrl` in params, deploy code separately:
```bash
# Option A: config-zip
az functionapp deployment source config-zip -g <rg> -n <funcName> --src ./cyera-connector.zip

# Option B: upload to blob and set run-from-package
./scripts/upload_function_package.sh <rg> <storageAccountName> <container> <funcName> ./cyera-connector.zip 24
```
