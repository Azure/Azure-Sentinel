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

2. **PR Validation Mode**:
   - Runs the bundling script to regenerate zip files
   - Checks if the zip files in the PR match the generated ones
   - **Fails the PR** if zip bundles are out of sync with source files
   - Provides clear instructions on how to update the bundles locally
   - PRs cannot be merged until bundles are up-to-date

3. **Prevents recursion** by:
   - Excluding zip file changes from triggering the workflow
   - Checking if the commit already contains zip updates

### Bundling Script

The `.script/bundleAwsS3Scripts.sh` script:

- Extracts existing zip files to preserve unchanged content
- Only replaces files that have been created or modified in the source directory
- Creates the nested zip file structure
- Handles the difference between Commercial (V2 Lambda) and Government (V1 Lambda) versions
- Ensures nothing is replaced that shouldn't be - only new/modified files are updated
- Cleans up temporary files after completion

## Files Included in Bundles

All bundles include:

- `AwsRequiredPolicies.md`
- `AwsRequiredPoliciesForGov.md`
- `CloudFormation/cloudformationtemplateforAWSS3.txt`
- `ConfigAwsConnector.ps1`
- `ConfigCloudTrailDataConnector.ps1`
- `ConfigCloudWatchDataConnector.ps1`
- `ConfigCustomLogDataConnector.ps1`
- `ConfigGuardDutyDataConnector.ps1`
- `ConfigVpcFlowDataConnector.ps1`
- `ConfigVpcFlowLogs.ps1`
- `Enviornment/EnviornmentConstants.ps1`
- `README.md`
- `Utils/AwsPoliciesUpdate.ps1`
- `Utils/AwsResourceCreator.ps1`
- `Utils/AwsSentinelTag.ps1`
- `Utils/CommonAwsPolicies.ps1`
- `Utils/HelperFunctions.ps1`

**Commercial bundles additionally include:**
- `CloudWatchLambdaFunction_V2.py`

**All bundles include:**
- `CloudWatchLambdaFunction.py`

## Manual Bundle Generation

If needed, you can manually regenerate the bundles:

```bash
# From the repository root
.script/bundleAwsS3Scripts.sh
```

Or trigger the workflow manually:

1. Go to the Actions tab in the GitHub repository
2. Select "AWS-S3 DataConnector Bundle Update" workflow
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

## Troubleshooting

### PR validation fails with "bundles are out of sync"

If your PR fails validation:

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
3. The PR validation will pass on the next run

### Workflow doesn't trigger

- Ensure changes are in the monitored paths (see above)
- For PRs: Check that the PR targets the `master` branch
- For auto-updates: Check that the changes were pushed to the `master` branch
- Verify the workflow file exists and is valid YAML

### Bundles are outdated

- Manually trigger the workflow from the Actions tab
- Or run the bundling script locally and commit the results

### Recursion issues

If the workflow triggers itself repeatedly:

- Check that the commit message includes `[skip ci]`
- Verify the workflow doesn't trigger on zip file changes
- Review the `check_changes` step logic in the workflow

## Development Notes

### Adding New Files to Bundles

To add new files to the bundles, edit `.script/bundleAwsS3Scripts.sh`:

1. Add the file path to the `FILES_TO_BUNDLE` array
2. Test locally: `.script/bundleAwsS3Scripts.sh`
3. Commit the script change

The workflow will automatically include the new file in future bundles.

### Modifying Bundle Structure

To change which files go in which bundle variant (Commercial vs. Government):

1. Edit the `create_nested_zip` function in `.script/bundleAwsS3Scripts.sh`
2. Adjust the logic for `lambda_version` parameter
3. Test locally before committing

## Benefits

✅ **Consistency**: Bundles are always in sync with source files
✅ **Automation**: No manual zip file creation needed
✅ **Transparency**: All changes are tracked in Git
✅ **Reliability**: Automated testing ensures bundles are created correctly
✅ **Documentation**: Clear process for maintenance and updates
