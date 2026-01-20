#!/bin/bash
# Script to bundle AWS-S3 DataConnector scripts into zip files
# This script creates the ConfigAwsS3DataConnectorScripts.zip and ConfigAwsS3DataConnectorScriptsGov.zip files
# It extracts existing zips and only replaces modified files to preserve unchanged content

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

# Get list of changed files in the AWS-S3 directory from the last commit
get_changed_files() {
    local base_ref="${GITHUB_BASE_REF:-HEAD~1}"  # Use GitHub base ref or previous commit
    local changed_files=()
    
    # Get all changed files in the AWS-S3 directory, excluding zip files
    while IFS= read -r file; do
        # Skip if no file (empty output from git diff)
        [[ -z "$file" ]] && continue
        
        # Skip zip files and BUNDLE_AUTOMATION.md (documentation only)
        [[ "$file" == *.zip ]] && continue
        [[ "$file" == *"BUNDLE_AUTOMATION.md" ]] && continue
        
        # Remove the DataConnectors/AWS-S3/ prefix to get relative path
        local relative_file="${file#DataConnectors/AWS-S3/}"
        if [[ "$relative_file" != "$file" ]] && [[ -n "$relative_file" ]]; then  # File is in AWS-S3 directory and not empty
            changed_files+=("$relative_file")
        fi
    done < <(git diff --name-only "$base_ref" HEAD -- "DataConnectors/AWS-S3/" 2>/dev/null || true)
    
    # Only output if we have files
    if [[ ${#changed_files[@]} -gt 0 ]]; then
        printf '%s\n' "${changed_files[@]}"
    fi
}

# Replace the hardcoded FILES_TO_BUNDLE with dynamic detection
mapfile -t FILES_TO_BUNDLE < <(get_changed_files)

# Fallback: if no files changed, include all relevant files
if [[ ${#FILES_TO_BUNDLE[@]} -eq 0 ]]; then
    echo "No changes detected, including all files..."
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
else
    echo "Detected ${#FILES_TO_BUNDLE[@]} changed file(s) to update in bundles:"
    printf '  - %s\n' "${FILES_TO_BUNDLE[@]}"
fi

# Function to extract existing zip if it exists, or create empty directory
extract_or_create() {
    local zip_path="$1"
    local extract_dir="$2"
    
    mkdir -p "$extract_dir"
    
    if [ -f "$zip_path" ]; then
        echo "  Extracting existing $zip_path..."
        unzip -q "$zip_path" -d "$extract_dir" 2>/dev/null || true
    else
        echo "  Creating new bundle (no existing zip found)..."
    fi
}

# Function to update files in directory (only replace if source exists and is different)
update_files() {
    local dest_dir="$1"
    shift
    local files=("$@")
    
    for file in "${files[@]}"; do
        if [ -f "$AWS_S3_DIR/$file" ]; then
            local dir_path=$(dirname "$dest_dir/$file")
            mkdir -p "$dir_path"
            # Only copy if file doesn't exist or is different
            if [ ! -f "$dest_dir/$file" ] || ! cmp -s "$AWS_S3_DIR/$file" "$dest_dir/$file"; then
                cp "$AWS_S3_DIR/$file" "$dest_dir/$file"
                echo "  Updated: $file"
            fi
        else
            echo "  Warning: File not found in source: $file"
        fi
    done
}

# Function to create a nested zip file
create_nested_zip() {
    local parent_zip="$1"
    local nested_zip_name="$2"
    local work_dir="$3"
    local lambda_version="$4"  # "v1" or "v2"
    
    echo "Processing $nested_zip_name..."
    
    # Create temporary directory for this nested zip
    local nested_dir="$work_dir/${nested_zip_name%.zip}"
    
    # Extract existing nested zip from parent if it exists
    if [ -f "$AWS_S3_DIR/$parent_zip" ]; then
        local parent_extract="$work_dir/parent_extract"
        mkdir -p "$parent_extract"
        unzip -q "$AWS_S3_DIR/$parent_zip" -d "$parent_extract" 2>/dev/null || true
        
        if [ -f "$parent_extract/$nested_zip_name" ]; then
            extract_or_create "$parent_extract/$nested_zip_name" "$nested_dir"
        else
            mkdir -p "$nested_dir"
        fi
        rm -rf "$parent_extract"
    else
        mkdir -p "$nested_dir"
    fi
    
    # Update common files (only replace modified ones)
    update_files "$nested_dir" "${FILES_TO_BUNDLE[@]}"
    
    # Update appropriate Lambda function version
    if [ "$lambda_version" = "v2" ]; then
        if [ -f "$AWS_S3_DIR/CloudWatchLambdaFunction.py" ]; then
            if [ ! -f "$nested_dir/CloudWatchLambdaFunction.py" ] || ! cmp -s "$AWS_S3_DIR/CloudWatchLambdaFunction.py" "$nested_dir/CloudWatchLambdaFunction.py"; then
                cp "$AWS_S3_DIR/CloudWatchLambdaFunction.py" "$nested_dir/CloudWatchLambdaFunction.py"
                echo "  Updated: CloudWatchLambdaFunction.py"
            fi
        fi
        if [ -f "$AWS_S3_DIR/CloudWatchLambdaFunction_V2.py" ]; then
            if [ ! -f "$nested_dir/CloudWatchLambdaFunction_V2.py" ] || ! cmp -s "$AWS_S3_DIR/CloudWatchLambdaFunction_V2.py" "$nested_dir/CloudWatchLambdaFunction_V2.py"; then
                cp "$AWS_S3_DIR/CloudWatchLambdaFunction_V2.py" "$nested_dir/CloudWatchLambdaFunction_V2.py"
                echo "  Updated: CloudWatchLambdaFunction_V2.py"
            fi
        fi
    else
        if [ -f "$AWS_S3_DIR/CloudWatchLambdaFunction.py" ]; then
            if [ ! -f "$nested_dir/CloudWatchLambdaFunction.py" ] || ! cmp -s "$AWS_S3_DIR/CloudWatchLambdaFunction.py" "$nested_dir/CloudWatchLambdaFunction.py"; then
                cp "$AWS_S3_DIR/CloudWatchLambdaFunction.py" "$nested_dir/CloudWatchLambdaFunction.py"
                echo "  Updated: CloudWatchLambdaFunction.py"
            fi
        fi
        # Remove V2 if it exists (shouldn't be in gov bundles)
        if [ -f "$nested_dir/CloudWatchLambdaFunction_V2.py" ]; then
            rm "$nested_dir/CloudWatchLambdaFunction_V2.py"
            echo "  Removed: CloudWatchLambdaFunction_V2.py (not needed for gov)"
        fi
    fi
    
    # Create the zip file
    cd "$nested_dir"
    zip -q -r "$work_dir/$nested_zip_name" . -i "*"
    
    # Clean up nested directory
    rm -rf "$nested_dir"
    
    echo "✓ Created $nested_zip_name"
}

# Create ConfigAwsS3DataConnectorScripts.zip (Commercial Azure - includes V2)
echo ""
echo "Building ConfigAwsS3DataConnectorScripts.zip..."
create_nested_zip "ConfigAwsS3DataConnectorScripts.zip" "ConfigAwsComToAzureCom.zip" "$TEMP_DIR/com" "v2"
create_nested_zip "ConfigAwsS3DataConnectorScripts.zip" "ConfigAwsGovToAzureCom.zip" "$TEMP_DIR/com" "v2"

cd "$TEMP_DIR/com"
zip -q "ConfigAwsS3DataConnectorScripts.zip" ConfigAwsComToAzureCom.zip ConfigAwsGovToAzureCom.zip
cp "ConfigAwsS3DataConnectorScripts.zip" "$AWS_S3_DIR/"
echo "✓ Created ConfigAwsS3DataConnectorScripts.zip"

# Create ConfigAwsS3DataConnectorScriptsGov.zip (Government Azure - no V2)
echo ""
echo "Building ConfigAwsS3DataConnectorScriptsGov.zip..."
create_nested_zip "ConfigAwsS3DataConnectorScriptsGov.zip" "ConfigAwsComToAzureGov.zip" "$TEMP_DIR/gov" "v1"
create_nested_zip "ConfigAwsS3DataConnectorScriptsGov.zip" "ConfigAwsGovToAzureGov.zip" "$TEMP_DIR/gov" "v1"

cd "$TEMP_DIR/gov"
zip -q "ConfigAwsS3DataConnectorScriptsGov.zip" ConfigAwsComToAzureGov.zip ConfigAwsGovToAzureGov.zip
cp "ConfigAwsS3DataConnectorScriptsGov.zip" "$AWS_S3_DIR/"
echo "✓ Created ConfigAwsS3DataConnectorScriptsGov.zip"

echo ""
echo "✅ Successfully created all AWS-S3 DataConnector script bundles!"
echo "   - ConfigAwsS3DataConnectorScripts.zip"
echo "   - ConfigAwsS3DataConnectorScriptsGov.zip"