#!/usr/bin/env bash
# package.sh - build a deployable Sentinel solution package (.zip) for this solution.
#
# Replicates the official Azure-Sentinel packaging pipeline output
# (.script/package-automation/package-generator.ps1 -> createSolutionV4.ps1
#  -> commonFunctions.ps1 GeneratePackage), which produces a zip containing
# exactly two files at the archive root:
#   - mainTemplate.json       (ARM template with all solution resources)
#   - createUiDefinition.json (portal UI for the deployment flow)
#
# The resulting zip can be:
#   1. Uploaded to a storage account and deployed via the Azure portal
#      "Template deployment" -> "Edit template" -> "Load file",
#   2. Deployed with the az CLI / REST "solution" deployment API, or
#   3. Submitted to Microsoft's Sentinel solution catalog pipeline (the
#      .ps1 path is used by the Azure-Sentinel CI for that).
#
# Usage:
#   ./package.sh                 # version taken from mainTemplate _solutionVersion
#   ./package.sh 3.0.2           # explicit version
#
# Output: Package/<version>.zip

set -euo pipefail

SOLUTION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PKG_DIR="$SOLUTION_DIR/Package"

cd "$PKG_DIR"

# --- locate / validate inputs -------------------------------------------------
for f in mainTemplate.json createUiDefinition.json; do
    if [[ ! -f "$f" ]]; then
        echo "ERROR: $PKG_DIR/$f not found" >&2
        exit 1
    fi
done

# Validate both files are well-formed JSON before packaging
for f in mainTemplate.json createUiDefinition.json; do
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "import json,sys; json.load(open('$f'))" || { echo "ERROR: $f is not valid JSON" >&2; exit 1; }
    fi
done

# --- determine package version -------------------------------------------------
if [[ $# -ge 1 ]]; then
    VERSION="$1"
else
    VERSION=$(python3 - <<'PY'
import json
t = json.load(open('mainTemplate.json'))
# The solution version variable is defined as "_solutionVersion" in every
# Sentinel solution ARM template (see variables block).
v = t.get('variables', {}).get('_solutionVersion')
if v is None:
    raise SystemExit("ERROR: variables._solutionVersion not found in mainTemplate.json")
print(v)
PY
)
    if [[ -z "$VERSION" ]]; then
        echo "ERROR: could not determine version" >&2
        exit 1
    fi
fi

OUT="$VERSION.zip"

# --- build the zip (files at archive root, matching the official pipeline) -----
rm -f "$OUT"
if command -v zip >/dev/null 2>&1; then
    zip -j -X "$OUT" mainTemplate.json createUiDefinition.json > /dev/null
elif command -v Compress-Archive >/dev/null 2>&1; then
    Compress-Archive -Path mainTemplate.json, createUiDefinition.json -DestinationPath "$OUT" -Force
elif command -v python3 >/dev/null 2>&1; then
    python3 - "$OUT" <<'PY'
import sys, zipfile
out = sys.argv[1]
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in ('mainTemplate.json', 'createUiDefinition.json'):
        z.write(f, f)
PY
else
    echo "ERROR: need zip, Compress-Archive, or python3" >&2
    exit 1
fi

echo "Created $PKG_DIR/$OUT"
echo "Contents:"
if command -v unzip >/dev/null 2>&1; then
    unzip -l "$OUT"
fi

# --- deploy hint ----------------------------------------------------------------
cat <<EOF

To deploy this package to a workspace:
  # 1. via az CLI (deployment at resource-group scope):
  az deployment group create \\
    --resource-group <rg> \\
    --template-file "$PKG_DIR/mainTemplate.json" \\
    --parameters workspace=<workspace-name> workspace-location=<region> \\
                 location=<region> resourceGroupName=<rg> subscription=<sub-id>

  # 2. or upload $OUT to a storage blob and deploy from the portal
  #    (Template spec / "Edit template" -> "Load file").
EOF
