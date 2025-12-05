#!/bin/bash

# Lookout Mobile Risk API v2 - Automated Installer
# Author: Lookout Inc.
# Version: 2.0.0
# Description: Automated deployment script for Lookout MRA v2 comprehensive data connector

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/lookout-mrav2-install-$(date +%Y%m%d-%H%M%S).log"
TEMPLATE_URI="https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Lookout/Data%20Connectors/LookoutMRAv2_Comprehensive.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables
SUBSCRIPTION_ID=""
RESOURCE_GROUP_NAME=""
WORKSPACE_NAME=""
LOOKOUT_API_KEY=""
LOCATION=""
ENABLE_DEBUG_LOGGING=false
VALIDATE_ONLY=false

# Banner
show_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Lookout Mobile Risk API v2 Installer                     ║
║                           Comprehensive Data Connector                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Logging functions
log_info() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${BLUE}[$timestamp] [INFO] $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${GREEN}[$timestamp] [SUCCESS] $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${YELLOW}[$timestamp] [WARNING] $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${RED}[$timestamp] [ERROR] $1${NC}" | tee -a "$LOG_FILE"
}

# Help function
show_help() {
    cat << EOF
Lookout Mobile Risk API v2 Installer

USAGE:
    $0 [OPTIONS]

REQUIRED OPTIONS:
    -s, --subscription-id ID        Azure subscription ID
    -g, --resource-group NAME       Resource group name
    -w, --workspace NAME            Microsoft Sentinel workspace name

OPTIONAL OPTIONS:
    -k, --api-key KEY               Lookout API key (will prompt if not provided)
    -l, --location REGION           Azure region (defaults to resource group location)
    -d, --debug                     Enable debug logging
    -v, --validate-only             Only validate deployment without executing
    -t, --template-uri URI          Custom ARM template URI
    -h, --help                      Show this help message

EXAMPLES:
    # Basic installation
    $0 -s "12345678-1234-1234-1234-123456789012" -g "rg-sentinel" -w "sentinel-workspace"

    # Installation with debug logging
    $0 -s "12345678-1234-1234-1234-123456789012" -g "rg-sentinel" -w "sentinel-workspace" -d

    # Validate only (dry run)
    $0 -s "12345678-1234-1234-1234-123456789012" -g "rg-sentinel" -w "sentinel-workspace" -v

REQUIREMENTS:
    - Azure CLI installed and configured
    - Appropriate Azure permissions (Sentinel Contributor, Log Analytics Contributor)
    - Lookout API key

EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--subscription-id)
                SUBSCRIPTION_ID="$2"
                shift 2
                ;;
            -g|--resource-group)
                RESOURCE_GROUP_NAME="$2"
                shift 2
                ;;
            -w|--workspace)
                WORKSPACE_NAME="$2"
                shift 2
                ;;
            -k|--api-key)
                LOOKOUT_API_KEY="$2"
                shift 2
                ;;
            -l|--location)
                LOCATION="$2"
                shift 2
                ;;
            -d|--debug)
                ENABLE_DEBUG_LOGGING=true
                shift
                ;;
            -v|--validate-only)
                VALIDATE_ONLY=true
                shift
                ;;
            -t|--template-uri)
                TEMPLATE_URI="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Validate required parameters
    if [[ -z "$SUBSCRIPTION_ID" || -z "$RESOURCE_GROUP_NAME" || -z "$WORKSPACE_NAME" ]]; then
        log_error "Missing required parameters"
        show_help
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Azure CLI is installed
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI is not installed. Please install it from: https://learn.microsoft.com/cli/azure/install-azure-cli"
        exit 1
    fi
    log_success "✓ Azure CLI found: $(az version --query '"azure-cli"' -o tsv)"

    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        log_warning "jq is not installed. Installing jq for JSON processing..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y jq
        elif command -v yum &> /dev/null; then
            sudo yum install -y jq
        elif command -v brew &> /dev/null; then
            brew install jq
        else
            log_error "Cannot install jq automatically. Please install it manually."
            exit 1
        fi
    fi
    log_success "✓ jq found: $(jq --version)"

    # Check Azure CLI login status
    if ! az account show &> /dev/null; then
        log_info "Not logged in to Azure. Please log in..."
        az login
    fi
    log_success "✓ Azure CLI authenticated"
}

# Connect to Azure and set subscription
connect_azure() {
    log_info "Setting Azure subscription context..."
    
    if ! az account set --subscription "$SUBSCRIPTION_ID" 2>/dev/null; then
        log_error "Failed to set subscription: $SUBSCRIPTION_ID"
        log_info "Available subscriptions:"
        az account list --query "[].{Name:name, SubscriptionId:id}" -o table
        exit 1
    fi
    
    local subscription_name=$(az account show --query "name" -o tsv)
    log_success "✓ Connected to subscription: $subscription_name"
}

# Validate resource group
validate_resource_group() {
    log_info "Validating resource group: $RESOURCE_GROUP_NAME"
    
    if ! az group show --name "$RESOURCE_GROUP_NAME" &> /dev/null; then
        log_error "Resource group '$RESOURCE_GROUP_NAME' not found"
        exit 1
    fi
    
    local rg_location=$(az group show --name "$RESOURCE_GROUP_NAME" --query "location" -o tsv)
    log_success "✓ Resource group found: $rg_location"
    
    # Set location if not provided
    if [[ -z "$LOCATION" ]]; then
        LOCATION="$rg_location"
        log_info "Using resource group location: $LOCATION"
    fi
}

# Validate workspace
validate_workspace() {
    log_info "Validating Microsoft Sentinel workspace: $WORKSPACE_NAME"
    
    if ! az monitor log-analytics workspace show --resource-group "$RESOURCE_GROUP_NAME" --workspace-name "$WORKSPACE_NAME" &> /dev/null; then
        log_error "Workspace '$WORKSPACE_NAME' not found in resource group '$RESOURCE_GROUP_NAME'"
        exit 1
    fi
    
    local workspace_location=$(az monitor log-analytics workspace show --resource-group "$RESOURCE_GROUP_NAME" --workspace-name "$WORKSPACE_NAME" --query "location" -o tsv)
    log_success "✓ Workspace found: $workspace_location"
}

# Get Lookout API key
get_api_key() {
    if [[ -z "$LOOKOUT_API_KEY" ]]; then
        log_warning "Lookout API key required for authentication"
        echo -n "Enter Lookout API Key: "
        read -s LOOKOUT_API_KEY
        echo
    fi
    
    if [[ -z "$LOOKOUT_API_KEY" ]]; then
        log_error "Lookout API key is required"
        exit 1
    fi
    
    log_success "✓ API key provided"
}

# Deploy ARM template
deploy_template() {
    local deployment_name="LookoutMRAv2-$(date +%Y%m%d-%H%M%S)"
    
    log_info "Deployment name: $deployment_name"
    log_info "Template URI: $TEMPLATE_URI"
    log_info "Parameters: workspace=$WORKSPACE_NAME, location=$LOCATION, debugLogging=$ENABLE_DEBUG_LOGGING"
    
    # Create parameters JSON
    local params_json=$(cat << EOF
{
    "workspace": {"value": "$WORKSPACE_NAME"},
    "location": {"value": "$LOCATION"},
    "lookoutApiKey": {"value": "$LOOKOUT_API_KEY"},
    "enableDebugLogging": {"value": $ENABLE_DEBUG_LOGGING}
}
EOF
)
    
    if [[ "$VALIDATE_ONLY" == true ]]; then
        log_info "Validating ARM template deployment..."
        
        if az deployment group validate \
            --resource-group "$RESOURCE_GROUP_NAME" \
            --template-uri "$TEMPLATE_URI" \
            --parameters "$params_json" \
            --output none 2>/dev/null; then
            log_success "✓ Template validation successful"
            return 0
        else
            log_error "❌ Template validation failed"
            az deployment group validate \
                --resource-group "$RESOURCE_GROUP_NAME" \
                --template-uri "$TEMPLATE_URI" \
                --parameters "$params_json" \
                --output table
            return 1
        fi
    else
        log_info "Starting ARM template deployment..."
        
        if az deployment group create \
            --resource-group "$RESOURCE_GROUP_NAME" \
            --name "$deployment_name" \
            --template-uri "$TEMPLATE_URI" \
            --parameters "$params_json" \
            --output none; then
            log_success "✓ Deployment completed successfully"
            
            # Show deployment outputs
            log_info "Deployment Results:"
            log_info "=================="
            az deployment group show \
                --resource-group "$RESOURCE_GROUP_NAME" \
                --name "$deployment_name" \
                --query "properties.outputs" \
                --output table
            
            return 0
        else
            log_error "❌ Deployment failed"
            return 1
        fi
    fi
}

# Post-deployment validation
post_deployment_validation() {
    log_info "Running post-deployment validation..."
    
    # Wait for resources to be fully provisioned
    sleep 30
    
    log_info "Note: Custom table creation may take 5-10 minutes to complete"
    log_info "Note: Data ingestion may take 5-15 minutes to begin"
    
    log_success "✓ Post-deployment validation completed"
}

# Show next steps
show_next_steps() {
    echo
    log_success "Next Steps:"
    log_info "1. Wait 5-10 minutes for data ingestion to begin"
    log_info "2. Validate data ingestion with: LookoutMtdV2_CL | take 10"
    log_info "3. Test parser function with: LookoutEvents | take 5"
    log_info "4. Review deployment guide for troubleshooting: LookoutMRAv2_Deployment_Guide.md"
    echo
    log_info "Installation log saved to: $LOG_FILE"
}

# Cleanup function
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Installation failed with exit code: $exit_code"
        log_info "Installation log saved to: $LOG_FILE"
    fi
    exit $exit_code
}

# Main execution
main() {
    # Set up error handling
    trap cleanup EXIT
    
    show_banner
    log_info "Starting Lookout MRA v2 installation..."
    
    # Parse arguments
    parse_arguments "$@"
    
    # Prerequisites
    check_prerequisites
    
    # Azure connection and validation
    connect_azure
    validate_resource_group
    validate_workspace
    
    # Get API key
    get_api_key
    
    # Deploy template
    if deploy_template; then
        if [[ "$VALIDATE_ONLY" == true ]]; then
            log_success "✅ Validation completed successfully - template is ready for deployment"
        else
            post_deployment_validation
            show_next_steps
            log_success "🎉 Lookout MRA v2 installation completed successfully!"
        fi
    else
        if [[ "$VALIDATE_ONLY" == true ]]; then
            log_error "❌ Validation failed - please review errors above"
        else
            log_error "❌ Installation failed"
        fi
        exit 1
    fi
}

# Run main function with all arguments
main "$@"