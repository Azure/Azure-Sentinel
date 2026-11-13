#!/usr/bin/env bash
# Regenerates Package/mainTemplate.json + createUiDefinition.json via the official
# Azure/Azure-Sentinel createSolutionV3.ps1 tool, then runs ARM-TTK with the same
# false-positive filters Microsoft's own PR pipeline uses.
#
# Requires: pwsh (>=7.4), git, Install-Module powershell-yaml
#
# To prepare the Azure-Sentinel fork for PR submission:
#   cd ~/Phd/azure/Azure-Sentinel
#   git fetch upstream
#   git checkout -b feature/qcrypton-pqc-engine upstream/master
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-/tmp/sentinel-build}"
SENTINEL_REPO="$WORK/Azure-Sentinel"
BRANCH="feature/qcrypton-pqc-engine"
SOLUTION_NAME="QCryptonPQCEngine"
STAGE="$SENTINEL_REPO/Solutions/$SOLUTION_NAME"

command -v pwsh >/dev/null || { echo "pwsh not found"; exit 1; }
command -v git  >/dev/null || { echo "git not found";  exit 1; }
pwsh -NoProfile -Command "if (-not (Get-Module -ListAvailable powershell-yaml)) { Install-Module powershell-yaml -Scope CurrentUser -Force -AllowClobber }"

mkdir -p "$WORK"
if [ ! -d "$SENTINEL_REPO/.git" ]; then
  git clone --depth 1 --filter=blob:none --sparse https://github.com/Azure/Azure-Sentinel.git "$SENTINEL_REPO"
  (cd "$SENTINEL_REPO" && git sparse-checkout set Tools/Create-Azure-Sentinel-Solution .script)
fi

rm -rf "$STAGE"
mkdir -p "$STAGE/Data" "$STAGE/Data Connectors" "$STAGE/Analytic Rules" \
         "$STAGE/Workbooks" "$STAGE/Playbooks/QCryptonPQCEngine-Notify"

cp "$SRC/Data_Connectors/QCryptonPQCEngine_CCF/"*.json "$STAGE/Data Connectors/"
cp "$SRC/Analytic_Rules/"*.yaml                                      "$STAGE/Analytic Rules/"
cp "$SRC/Workbooks/QCryptonPQCEnginePosture.json"                    "$STAGE/Workbooks/"
cp "$SRC/Playbooks/QCryptonPQCEngine-Notify/azuredeploy.json"        "$STAGE/Playbooks/QCryptonPQCEngine-Notify/"
cp "$SRC/SolutionMetadata.json"                                      "$STAGE/"
cp "$SRC/ReleaseNotes.md"                                            "$STAGE/"

cat > "$STAGE/Data/Solution_$SOLUTION_NAME.json" <<JSON
{
  "Name": "$SOLUTION_NAME",
  "Author": "QCrypton, Inc.",
  "Logo": "<img src=\"https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/qcrypton.svg\" width=\"75px\" height=\"75px\">",
  "Description": "Runtime cryptographic telemetry from QCrypton PQC Engine, an OpenSSL 3.x provider for F5 BIG-IP that adds ML-KEM-768/1024 and ML-DSA-65/87 post-quantum algorithms. Ships with data connector, 6 analytic rules, workbook, and Teams-notification playbook.",
  "Data Connectors": ["Data Connectors/QCryptonPQCEngine_ConnectorDefinition.json"],
  "Workbooks":       ["Workbooks/QCryptonPQCEnginePosture.json"],
  "Analytic Rules":  [
    "Analytic Rules/PolicyBlockDetected.yaml",
    "Analytic Rules/VulnerableAlgorithmDetected.yaml",
    "Analytic Rules/PQCDowngradeOnEngine.yaml",
    "Analytic Rules/HighClassicalClientRate.yaml",
    "Analytic Rules/KEMOperationFailureSpike.yaml",
    "Analytic Rules/PolicyUpgradeActivity.yaml"
  ],
  "Playbooks":       ["Playbooks/QCryptonPQCEngine-Notify/azuredeploy.json"],
  "Metadata": "SolutionMetadata.json",
  "BasePath": "$STAGE",
  "Version": "1.0.0",
  "TemplateSpec": true,
  "Is1PConnector": false
}
JSON

echo ">>> Running createSolutionV3.ps1..."
( cd "$SENTINEL_REPO" && pwsh -NoProfile -File "Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1" \
    -SolutionDataFolderPath "$STAGE/Data" ) >/tmp/v3-build.log 2>&1 || true
grep -E "Fail=|Failed" /tmp/v3-build.log | tail -5 || true

echo ">>> Running ARM-TTK (Microsoft's filtered runner)..."
(cd "$SENTINEL_REPO" && pwsh -NoProfile -File .script/local-validation/run-arm-ttk.ps1 -SolutionPath "$STAGE") \
  | tee /tmp/arm-ttk.log | tail -5
grep "ARM-TTK-SUMMARY" /tmp/arm-ttk.log

echo ">>> Post-processing: friendly display name..."
python3 -c "
import json, sys
p = '$STAGE/Package/mainTemplate.json'
d = json.load(open(p))
for r in d['resources']:
    if r.get('type', '').endswith('contentPackages'):
        r['properties']['displayName'] = 'QCrypton PQC Engine'
json.dump(d, open(p, 'w'), indent=2)
print('  displayName set to: QCrypton PQC Engine')
"

echo ">>> Syncing Package back to $SRC/Package..."
rm -rf "$SRC/Package"
cp -r "$STAGE/Package" "$SRC/Package"
echo ">>> Done. Package contents:"
ls "$SRC/Package"
