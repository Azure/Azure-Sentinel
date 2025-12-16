#!/bin/bash
# Script to bundle AWS-S3 DataConnector scripts into zip files
# This script creates the ConfigAwsS3DataConnectorScripts.zip and ConfigAwsS3DataConnectorScriptsGov.zip files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AWS_S3_DIR="$REPO_ROOT/DataConnectors/AWS-S3"
TEMP_DIR=$(mktemp -d)

echo "Building AWS-S3 DataConnector script bundles..."
echo "Working directory: $TEMP_DIR"

cleanup() {
    echo "Cleaning up temporary directory..."
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

cd "$AWS_S3_DIR"

# Create temporary directories for building zips
mkdir -p "$TEMP_DIR/com" "$TEMP_DIR/gov"

# List of files to include in all bundles (relative paths from AWS_S3_DIR)
FILES_TO_BUNDLE=(
    "AwsRequiredPolicies.md"
    "AwsRequiredPoliciesForGov.md"
    "CloudFormation/cloudformationtemplateforAWSS3.txt"
    "ConfigAwsConnector.ps1"
    "ConfigCloudTrailDataConnector.ps1"
    "ConfigCloudWatchDataConnector.ps1"
    "ConfigCustomLogDataConnector.ps1"
    "ConfigGuardDutyDataConnector.ps1"
    "ConfigVpcFlowDataConnector.ps1"
    "ConfigVpcFlowLogs.ps1"
    "Enviornment/EnviornmentConstants.ps1"
    "README.md"
    "Utils/AwsPoliciesUpdate.ps1"
    "Utils/AwsResourceCreator.ps1"
    "Utils/AwsSentinelTag.ps1"
    "Utils/CommonAwsPolicies.ps1"
    "Utils/HelperFunctions.ps1"
)

# Function to copy files to a destination directory
copy_files() {
    local dest_dir="$1"
    shift
    local files=("$@")
    
    for file in "${files[@]}"; do
        if [ -f "$AWS_S3_DIR/$file" ]; then
            local dir_path=$(dirname "$dest_dir/$file")
            mkdir -p "$dir_path"
            cp "$AWS_S3_DIR/$file" "$dest_dir/$file"
        else
            echo "Warning: File not found: $file"
        fi
    done
}

# Function to create a nested zip file
create_nested_zip() {
    local zip_name="$1"
    local work_dir="$2"
    local lambda_version="$3"  # "v1" or "v2"
    
    echo "Creating $zip_name..."
    
    # Create temporary directory for this zip
    local nested_dir="$work_dir/${zip_name%.zip}"
    mkdir -p "$nested_dir"
    
    # Copy common files
    copy_files "$nested_dir" "${FILES_TO_BUNDLE[@]}"
    
    # Copy appropriate Lambda function version
    if [ "$lambda_version" = "v2" ]; then
        cp "$AWS_S3_DIR/CloudWatchLambdaFunction.py" "$nested_dir/CloudWatchLambdaFunction.py"
        cp "$AWS_S3_DIR/CloudWatchLambdaFunction_V2.py" "$nested_dir/CloudWatchLambdaFunction_V2.py"
    else
        cp "$AWS_S3_DIR/CloudWatchLambdaFunction.py" "$nested_dir/CloudWatchLambdaFunction.py"
    fi
    
    # Create the zip file (using backslashes for Windows compatibility)
    cd "$nested_dir"
    # Use zip with -r for recursive and preserve directory structure
    zip -q -r "$work_dir/$zip_name" . -i "*"
    
    # Clean up nested directory
    rm -rf "$nested_dir"
    
    echo "✓ Created $zip_name"
}

# Create ConfigAwsS3DataConnectorScripts.zip (Commercial Azure - includes V2)
echo ""
echo "Building ConfigAwsS3DataConnectorScripts.zip..."
create_nested_zip "ConfigAwsComToAzureCom.zip" "$TEMP_DIR/com" "v2"
create_nested_zip "ConfigAwsGovToAzureCom.zip" "$TEMP_DIR/com" "v2"

cd "$TEMP_DIR/com"
zip -q "ConfigAwsS3DataConnectorScripts.zip" ConfigAwsComToAzureCom.zip ConfigAwsGovToAzureCom.zip
cp "ConfigAwsS3DataConnectorScripts.zip" "$AWS_S3_DIR/"
echo "✓ Created ConfigAwsS3DataConnectorScripts.zip"

# Create ConfigAwsS3DataConnectorScriptsGov.zip (Government Azure - no V2)
echo ""
echo "Building ConfigAwsS3DataConnectorScriptsGov.zip..."
create_nested_zip "ConfigAwsComToAzureGov.zip" "$TEMP_DIR/gov" "v1"
create_nested_zip "ConfigAwsGovToAzureGov.zip" "$TEMP_DIR/gov" "v1"

cd "$TEMP_DIR/gov"
zip -q "ConfigAwsS3DataConnectorScriptsGov.zip" ConfigAwsComToAzureGov.zip ConfigAwsGovToAzureGov.zip
cp "ConfigAwsS3DataConnectorScriptsGov.zip" "$AWS_S3_DIR/"
echo "✓ Created ConfigAwsS3DataConnectorScriptsGov.zip"

echo ""
echo "✅ Successfully created all AWS-S3 DataConnector script bundles!"
echo "   - ConfigAwsS3DataConnectorScripts.zip"
echo "   - ConfigAwsS3DataConnectorScriptsGov.zip"
