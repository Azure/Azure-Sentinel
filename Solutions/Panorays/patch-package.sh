# Step 1: run the build as normal
pwsh ./createSolutionV3.ps1 -SolutionName "Panorays" \
  -InputFilePath "/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/Data/Panorays_Input.json" \
  -OutputDirectory "/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/Package"

# Step 2: patch the Package createUiDefinition.json outputs
python3 -c "
import json
path = '/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/Package/createUiDefinition.json'
with open(path) as f:
    ui = json.load(f)
ui['parameters']['outputs']['panoraysAPIBaseUrl'] = \"[steps('configuration').panoraysAPIBaseUrl]\"
ui['parameters']['outputs']['apitoken'] = \"[steps('configuration').apitoken]\"
with open(path, 'w') as f:
    json.dump(ui, f, indent=4)
print('Patched createUiDefinition.json outputs successfully')
"

# Step 3: patch the Package mainTemplate.json parameters
python3 -c "
import json
path = '/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/Package/mainTemplate.json'
with open(path) as f:
    t = json.load(f)
t['parameters']['apitoken'] = {
    'type': 'securestring',
    'metadata': {'description': 'API Token for authenticating with the Panorays API'}
}
t['parameters']['panoraysAPIBaseUrl'] = {
    'type': 'string',
    'defaultValue': 'https://api.panoraysapp.com',
    'metadata': {'description': 'Base URL for the Panorays API'}
}
with open(path, 'w') as f:
    json.dump(t, f, indent=4)
print('Patched mainTemplate.json parameters successfully')
"
# Step 3b: Remove unreferenced script-injected parameters
python3 -c "
import json
path = '/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/Package/mainTemplate.json'
with open(path) as f:
    t = json.load(f)
t['parameters'].pop('resourceGroupName', None)
t['parameters'].pop('subscription', None)
with open(path, 'w') as f:
    json.dump(t, f, indent=4)
print('Removed unreferenced parameters: resourceGroupName, subscription')
"

# Step 3c: Remove script-injected unreferenced TemplateEmptyArray variable
python3 -c "
import json
path = '/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/Package/mainTemplate.json'
with open(path) as f:
    t = json.load(f)
t['variables'].pop('TemplateEmptyArray', None)
with open(path, 'w') as f:
    json.dump(t, f, indent=4)
print('Removed TemplateEmptyArray variable')
"



echo "Build complete — ready to commit"
# Step 4: Regenerate the zip from the patched files

python3 -c "
import json
path = '/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/Package/mainTemplate.json'
with open(path) as f:
    t = json.load(f)
# Fix defaultValue for apitoken inside connections contentTemplate
for r in t['resources']:
    if r.get('type') == 'Microsoft.OperationalInsights/workspaces/providers/contentTemplates':
        mt = r.get('properties', {}).get('mainTemplate', {})
        if 'apitoken' in mt.get('parameters', {}):
            mt['parameters']['apitoken']['defaultValue'] = ''
with open(path, 'w') as f:
    json.dump(t, f, indent=4)
print('Fixed apitoken defaultValue in contentTemplate')
"

# Step 5: Regenerate the zip from the patched files
python3 -c "
import zipfile, os, glob

package_dir = '/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/Package'

old_zips = glob.glob(os.path.join(package_dir, '*.zip'))
for z in old_zips:
    os.remove(z)
    print(f'Removed old zip: {z}')

version = '3.0.0'
zip_path = os.path.join(package_dir, f'{version}.zip')

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for fname in ['mainTemplate.json', 'createUiDefinition.json']:
        fpath = os.path.join(package_dir, fname)
        zf.write(fpath, fname)
        print(f'Added to zip: {fname}')

print(f'Created: {zip_path}')
"