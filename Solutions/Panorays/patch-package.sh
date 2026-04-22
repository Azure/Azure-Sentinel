# Step 1: run the build as normal
pwsh ./createSolutionV3.ps1 -SolutionName "Panorays" \
  -InputFilePath "/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/Data/Panorays_Input.json" \
  -OutputDirectory "/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/Package"

# Step 2: Patch createUiDefinition.json - rename step and restore outputs
python3 -c "
import json
path = '/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/Package/createUiDefinition.json'
with open(path) as f:
    ui = json.load(f)

# Rename the script-generated 'dataconnectors' step to 'configuration'
# and restore the correct elements
for step in ui['parameters']['steps']:
    if step.get('name') == 'dataconnectors':
        step['name'] = 'configuration'
        step['label'] = 'Configuration'
        step['bladeTitle'] = 'Panorays Configuration'
        step['subLabel'] = {
            'preValidation': 'API Details',
            'postValidation': 'Done'
        }
        step['elements'] = [
            {
                'name': 'instructions',
                'type': 'Microsoft.Common.TextBlock',
                'options': {
                    'text': 'Please provide your Panorays API details. These will be used to configure the Data Connector automatically.'
                }
            },
            {
                'name': 'panoraysAPIBaseUrl',
                'type': 'Microsoft.Common.TextBox',
                'label': 'Panorays API Base URL',
                'toolTip': 'The base URL for the Panorays API.',
                'defaultValue': 'https://api.panoraysapp.com',
                'constraints': {
                    'required': True,
                    'regex': '^https://.+',
                    'validationMessage': 'Please enter a valid URL starting with https://'
                }
            },
            {
                'name': 'apitoken',
                'type': 'Microsoft.Common.PasswordBox',
                'label': {
                    'password': 'API Token',
                    'confirmPassword': 'Confirm API Token'
                },
                'toolTip': 'Your Panorays API Token.',
                'constraints': {
                    'required': True,
                    'regex': r'^\S+$',
                    'validationMessage': 'The API Token must not contain spaces.'
                },
                'options': {
                    'hideConfirmation': True
                },
                'visible': True
            }
        ]
        print('Renamed dataconnectors step to configuration and restored elements')
        break

# Restore outputs
ui['parameters']['outputs']['panoraysAPIBaseUrl'] = \"[steps('configuration').panoraysAPIBaseUrl]\"
ui['parameters']['outputs']['apitoken'] = \"[steps('configuration').apitoken]\"

with open(path, 'w') as f:
    json.dump(ui, f, indent=4)
print('Patched createUiDefinition.json')
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