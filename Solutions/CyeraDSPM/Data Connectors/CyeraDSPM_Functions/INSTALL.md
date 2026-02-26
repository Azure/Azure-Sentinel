# Cyera DSPM for Microsoft Sentinel — v5 Install Pack

This pack deploys the v5 integration using **DCE + DCR (Direct)** and custom **Log Analytics tables**.

## Prereqs
- Azure CLI (`az`) logged in
- `jq` installed
- Existing Log Analytics Workspace

## 1) Configure env
```bash
cd scripts
cp 00_env.sample 00_env.sh && $EDITOR 00_env.sh
. ./00_env.sh
```

## 2) Create/Update tables
```bash
./10_put_tables.sh
```

## 3) Create/Update DCR (Direct)
```bash
./20_put_dcr.sh
```

## 4) Verify resources
```bash
./30_show_resources.sh
```
Ensure:
- `immutableId` is non-empty
- `dataCollectionEndpointId` shows your DCE ARM ID
- DCE `logsIngestion.endpoint` is a real URL

Optionally export the immutableId for seeding:
```bash
export DCR_IMMUTABLE_ID=$(az monitor data-collection rule show -g "$RG" -n "$DCR_NAME" --query properties.immutableId -o tsv)
```

## 5) (Optional) Seed sample data
```bash
./40_seed_samples.sh
```

## 6) Validate in Logs
Open `scripts/50_verify.kql` and run the queries in the Logs blade.
