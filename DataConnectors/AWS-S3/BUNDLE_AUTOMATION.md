# AWS-S3 DataConnector Scripts Bundle Automation

## Overview

The AWS-S3 DataConnector scripts are automatically bundled into zip files whenever changes are made to the source files. This automation ensures that the distributed zip files are always up-to-date with the latest script changes.

## Automated Bundles

Two main zip files are automatically maintained:

1. **ConfigAwsS3DataConnectorScripts.zip** - For Commercial Azure
   - Contains: `ConfigAwsComToAzureCom.zip` and `ConfigAwsGovToAzureCom.zip`
   - Includes both `CloudWatchLambdaFunction.py` and `CloudWatchLambdaFunction_V2.py`

2. **ConfigAwsS3DataConnectorScriptsGov.zip** - For Government Azure
   - Contains: `ConfigAwsComToAzureGov.zip` and `ConfigAwsGovToAzureGov.zip`
   - Includes only `CloudWatchLambdaFunction.py` (V1)

## How It Works

### GitHub Actions Workflow

The automation is implemented via a GitHub Actions workflow (`.github/workflows/aws-s3-bundle-update.yaml`) that:

1. **Triggers automatically** on:
   - **Pull Requests** targeting the `master` branch
   - When changes affect:
     - `*.ps1` files in the AWS-S3 directory
     - `*.py` files in the AWS-S3 directory
     - `*.md` files in the AWS-S3 directory
     - Files in `CloudFormation/`, `Enviornment/`, or `Utils/` subdirectories

2. **Auto-Update Mode**:
   - Runs the bundling script to regenerate zip files
   - Automatically commits updated bundles to the PR branch
   - Includes `[skip ci]` flag to prevent workflow recursion
   - Developers don't need to manually update bundles - it's handled automatically
   - Commits are made by GitHub Action bot with clear description

3. **Prevents recursion** by:
   - Excluding zip file changes from triggering the workflow
   - Checking if the commit already contains zip updates
   - Using `[skip ci]` flag in auto-commit messages

### Bundling Script

The `.script/bundleAwsS3Scripts.sh` script uses intelligent, dynamic bundling:

- **Dynamic File Detection**: Automatically detects changed files using `git diff`
  - Respects `GITHUB_BASE_REF` in CI/CD environments
  - Falls back to `HEAD~1` for local execution
  - Filters out `.zip` files and documentation automatically
- **Intelligent Updates**: Extracts existing zip files and only replaces modified files
  - Uses `cmp -s` to compare file contents
  - Preserves unchanged files to minimize bundle changes
- **Variant Handling**: Automatically manages differences between Commercial and Government bundles
  - Commercial: Includes both Lambda V1 and V2
  - Government: Includes only Lambda V1
- **Nested Structure**: Creates proper nested zip file structure
- **Fallback Safety**: If no changes detected, bundles all relevant files to ensure completeness

## Files Included in Bundles

The bundling script uses **dynamic file detection** to automatically determine which files to include:

### Dynamic Detection Process

1. **Changed Files Detection**: The script uses `git diff` to detect files that have been modified in the AWS-S3 directory
2. **Automatic Filtering**: Excludes `.zip` files and `BUNDLE_AUTOMATION.md` from the bundle
3. **Fallback Mechanism**: If no changes are detected, all relevant files in the AWS-S3 directory are bundled

### File Types Included

The script automatically bundles:
- **PowerShell scripts** (`*.ps1`) - Configuration and connector scripts
- **Python files** (`*.py`) - Lambda functions
- **Markdown documentation** (`*.md`) - Policy and usage documentation  
- **CloudFormation templates** - Infrastructure-as-code definitions
- **Utility scripts** - Helper functions and shared code in `Utils/` directory
- **Environment configuration** - Settings in `Enviornment/` directory

### Bundle Variants

**Commercial Azure Bundles** (`ConfigAwsS3DataConnectorScripts.zip`):
- Include both `CloudWatchLambdaFunction.py` and `CloudWatchLambdaFunction_V2.py`
- Contain two nested zips: `ConfigAwsComToAzureCom.zip` and `ConfigAwsGovToAzureCom.zip`

**Government Azure Bundles** (`ConfigAwsS3DataConnectorScriptsGov.zip`):
- Include only `CloudWatchLambdaFunction.py` (V1)
- Contain two nested zips: `ConfigAwsComToAzureGov.zip` and `ConfigAwsGovToAzureGov.zip`

### Adding New Files

Simply add or modify files in the `DataConnectors/AWS-S3/` directory. The bundling script will automatically detect and include them - no manual configuration needed!

## Manual Bundle Generation

If needed, you can manually regenerate the bundles:

```bash
# From the repository root
.script/bundleAwsS3Scripts.sh
```

Or trigger the workflow manually:

1. Go to the Actions tab in the GitHub repository
2. Select "AWS-S3 DataConnector Bundle Auto-Update" workflow
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

## Troubleshooting

### Bundles not auto-updated in PR

If bundles aren't automatically updated:

1. Check the GitHub Actions tab to see if the workflow ran
2. Verify your changes are in monitored paths (*.ps1, *.py, *.md, CloudFormation/, Enviornment/, Utils/)
3. If workflow succeeded but no commit appeared, bundles may already be up-to-date
4. Manually trigger the workflow from the Actions tab if needed

### Manual bundle update needed

If you prefer to update bundles manually or workflow fails:

1. Run the bundling script locally:
   ```bash
   .script/bundleAwsS3Scripts.sh
   ```
2. Commit the updated zip files:
   ```bash
   git add DataConnectors/AWS-S3/*.zip
   git commit -m "Update AWS-S3 bundles"
   git push
   ```

### Workflow doesn't trigger

- Ensure changes are in the monitored paths (see above)
- Check that the PR targets the `master` branch
- Verify the workflow file exists and is valid YAML
- Check that zip files weren't the only changes (they're excluded from triggers)

### Recursion issues

If the workflow triggers itself repeatedly:

- Check that the commit message includes `[skip ci]`
- Verify the workflow doesn't trigger on zip file changes
- Review the `check_changes` step logic in the workflow

## Development Notes

### Adding New Files to Bundles

**No configuration needed!** The bundling script uses dynamic file detection:

1. Simply add or modify files in the `DataConnectors/AWS-S3/` directory
2. The script automatically detects changes via `git diff`
3. New files are automatically included in the next bundle generation

The script intelligently handles:
- New PowerShell scripts (`*.ps1`)
- New Python files (`*.py`)
- New documentation (`*.md`)
- New files in `CloudFormation/`, `Enviornment/`, or `Utils/` subdirectories

### Modifying Bundle Structure

To change which files go in which bundle variant (Commercial vs. Government):

1. Edit the `create_nested_zip` function in `.script/bundleAwsS3Scripts.sh`
2. Adjust the logic for the `lambda_version` parameter
3. Test locally: `.script/bundleAwsS3Scripts.sh`
4. Commit your changes

### Understanding Dynamic Detection

The script's `get_changed_files()` function:
- Compares current branch against base branch (in PRs) or last commit (locally)
- Automatically filters out `.zip` files and `BUNDLE_AUTOMATION.md`
- Falls back to including all files if no changes are detected
- Works seamlessly in both CI/CD and local development environments

## Benefits

✅ **Consistency**: Bundles are always in sync with source files
✅ **Automation**: No manual zip file creation needed
✅ **Transparency**: All changes are tracked in Git
✅ **Reliability**: Automated testing ensures bundles are created correctly
✅ **Documentation**: Clear process for maintenance and updates
