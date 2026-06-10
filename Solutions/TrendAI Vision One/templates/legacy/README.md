# Legacy Templates

This folder contains legacy/archived templates for historical reference.

## Contents

### Workbench Templates
- `arm-template-workbench-compatibleSchema.json` - Old Workbench connector (compatible schema)
- `arm-template-workbench-newSchema.json` - Old Workbench connector (new schema)
- `arm-template-workbench-microsoft-pattern.json` - Monolithic Workbench template
- `deploy-parser-function.json` - Standalone parser function deployment

### OAT Templates
- `arm-template-oat-compatibleSchema.json` - Old OAT connector (compatible schema)
- `arm-template-oat-newSchema.json` - Old OAT connector (new schema)

## Notice

⚠️ **These templates are deprecated**

Please use the new modular templates:
- **Workbench**: `templates/workbench/` 
- **OAT**: `templates/oat/`

Both follow Microsoft's recommended modular architecture pattern with Deploy to Azure buttons.

## Migration

If you have deployed using these legacy templates, you can:

1. Keep existing deployments (they will continue to work)
2. Deploy new modular templates to a different workspace
3. Migrate by deleting old resources and deploying new modular solution

For migration assistance, please open an issue in the repository.
