#!/usr/bin/env bash

set -Eeuo pipefail

_msg() {  
  echo >&2 -e "${1-}"  
}

_msg_print() {
  echo >&2 -n -e "${1-}"
}

_msg_warning() {
  echo >&2 -e "\033[0;33m$1\033[0m"
}

_msg_error() {
  echo >&2 -e "\033[0;31m$1\033[0m"
}

_msg_success() {
  echo >&2 -e "\033[0;32m$1\033[0m"
}

_shout() {
  _msg
  echo >&2 "$(tput bold)${*}$(tput sgr0)"
  _msg
}

_die() {
  local msg=$1
  local code=${2-1} # default exit status 1
  _msg_error "😢  $msg"
  exit "$code"
}

_solution_data_folder_path="./Solutions/Tanium/Data"
_package_folder_path="./Solutions/Tanium/Package"


build_solution() {
  pwsh ./Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1 "$_solution_data_folder_path"

  _msg "💪 checking arm-ttk results"

  _msg "  🕵️  did the arm-ttk check pass?" 
    
  _msg "*********************************************************************************************************************"
  _msg "**  NOTE: "
  _msg "**"
  _msg "**      The following error is an IGNORABLE error"
  _msg "**      \033[0;31mProperty: \"id\" must use one of the following expressions for an resourceId property\033[0m"
  _msg "**      Citation: https://github.com/Azure/Azure-Sentinel/tree/e92286da7d185c99c6d30c2cb8c86bbeca1a99ba/Tools/Create-Azure-Sentinel-Solution/V3#arm-ttk-failue-for-contentproductid-id-issues"
  _msg "*********************************************************************************************************************"

  read -p "Enter Y if they passed: " ttk_passed

  if [ "$ttk_passed" != "Y" ] && [ "$ttk_passed" != "y" ]; then
    return 1
  fi

  _msg "\n📄 checking package json file validation"

  _msg "  🕵️  were all the package json files valid?" 
  read -p "    Enter Y if they were all valid: " json_passed

  if [ "$json_passed" != "Y" ] && [ "$json_passed" != "y" ]; then
    return 1
  fi

  _msg "\n📦 checking package build result"

  current_published_version=$(pwsh ./Solutions/Tanium/get-offer-id.ps1 "$_solution_data_folder_path")
  _msg "  🏷️  current published version is ${current_published_version}"
  read -p "    what version was built? " built_version

  if [ "$current_published_version" == "$built_version" ]; then
    _msg_error "New version was not published! Did you forget to increment?"
    return 1
  fi

  _msg "\n🚀 deploying to azure for review"

  read -p "    resource group: " target_resource_group
  read -p "    log analytics workspace: " target_workspace
  read -p "    workspace location: " target_location

  # TODO Now push up the templates to the demo/qa environment for review
  if ( ! az deployment group create \
    --resource-group "$target_resource_group" \
    --name "${built_version}-Preview${RANDOM}"  \
    --template-file "${_package_folder_path}/mainTemplate.json" \
    --parameters workspace-location="${target_location}" \
    --parameters workspace="${target_workspace}" \
    --parameters workbook1-name="Tanium Workbook v${built_version}" \
    --output none ) then
      _msg_error "Deployment failed! Check resource group activity for details."
      return 1
  fi

  _msg_warning "\n⚠️ Please verify all the template data in the the workspace ${target_workspace} and complete any final QA tasks."
}

check-command() {
  _msg "  🔧 checking $1"
  if ! command -v "$1" >/dev/null; then
    _die "$1 command not found: please brew install ${2-:$1}"
  fi
}

check-arm-ttk() {
  _msg "  🔧 checking arm-ttk module in powershell"
  if ! pwsh -c Get-Module arm-ttk | grep -q arm-ttk; then
    _die "arm-ttk module not found in your powershell"
  fi
}

# Verifies that all items are being included in the solution as expected. By
#  1. Checking that all files of the specified contribution type are in the manifest
#  2. Checking that all items declared in the manifest exist in the expected folder
_validate_solution_resources() {
  local contribution_type=$1
  local expected_folder=$2
  local expected_file_type=$3
  local display_icon=$4

  local actual_files      # The files we found in the expected location
  local declared_files    # The list of files from the manifest
  local undeclared_files  # Files we found that are not listed in the manifest
  local missing_files     # Files listed in the manifest, that we did not find

  _msg "  ${display_icon}  ${contribution_type}s"

  local json_property
  json_property=".\"${expected_folder}\"[]"

  actual_files=$(find "Solutions/Tanium/${expected_folder}" -name "*.${expected_file_type}" ! -name connect-module-connections.json | sort | sed -e 's|Solutions/Tanium/||')
  declared_files=$(jq -r "$json_property" Solutions/Tanium/Data/Solution_Tanium.json | sort)

  _msg "    🕵️  checking all files are all declared in the manifest"
  # comm -23 : omit lines in common and lines only in the second file
  undeclared_files=$(comm -23 <(echo "$actual_files") <(echo "$declared_files"))
  if [[ -n "$undeclared_files" ]]; then
    _msg_error "Found undeclared ${contribution_type} files:"
    _msg "$undeclared_files"
    _msg
    _msg "Did you forget to add them to Solutions/Tanium/Data/Solution_Tanium.json?"
    _msg
    exit 1  
  fi

  _msg "    🕵️  checking all ${contribution_type}s have a json file"
  # comm -13 : omit lines in common and lines only in the first file
  missing_files=$(comm -13 <(echo "$actual_files") <(echo "$declared_files"))
  if [[ -n "$missing_files" ]]; then
    _msg_error "Found ${contribution_type} files in Data/Solution_Tanium.json but missing the actual file:"
    _msg "$missing_files"
    _msg
    _msg "Did you forget to add them to Solutions/Tanium/${expected_folder}?"
    _msg
    exit 1 
  fi
}

# Verifies that all playbooks are being included in the solution as expected. By
#  1. Checking that all azuredeploy.json files under the /Solutions/Tanium/Playbooks folder are in the /Solutions/Tanium/Data/Solution_Tanium.json file
#  2. Checking that all playbooks declared in /Solutions/Tanium/Data/Solution_Tanium.json exist in /Solutions/Tanium/Playbooks
check-matching-playbook-declarations() {
  if ! _validate_solution_resources "playbook" "Playbooks" "json" "📒" ; then
    return 1
  fi
}


# Verifies that all workbooks are being included in the solution as expected. By
#  1. Checking that all .json files under the /Solutions/Tanium/Workbooks folder are in the /Solutions/Tanium/Data/Solution_Tanium.json file
#  2. Checking that all workbooks declared in /Solutions/Tanium/Data/Solution_Tanium.json exist in /Solutions/Tanium/Workbooks
check-matching-workbook-declarations() {
  if ! _validate_solution_resources "workbook" "Workbooks" "json" "📊" ; then
    return 1
  fi
}

# Verifies that all analytic rules are being included in the solution as expected. By
#  1. Checking that all .yaml files under the /Solutions/Tanium/Analytic Rules folder are in the /Solutions/Tanium/Data/Solution_Tanium.json file
#  2. Checking that all analytic rules declared in /Solutions/Tanium/Data/Solution_Tanium.json exist in /Solutions/Tanium/Analytic Rules
check-matching-analytic-rules-declarations() {
  if ! _validate_solution_resources "analytic rule" "Analytic Rules" "yaml" "🔎" ; then
    return 1
  fi
}

check_spelling(){

  local has_errors  
  if ! cspell --quiet ./Solutions/Tanium --exclude ./Solutions/Tanium/Workbooks/connect-module-connections.json --exclude ./Solutions/Tanium/Package/mainTemplate.json ; then
    
    _msg "  🕵️  Are the only misspellings variables names due to javascript limitations?"   
    read -p "Enter Y to continue: " ignore_spelling_errors
    if [ "$ignore_spelling_errors" != "Y" ] && [ "$ignore_spelling_errors" != "y" ]; then
      return 1
    fi

  fi  
}

check_prerequisites() {
  _msg "🧰 checking prerequisites"
  check-command "jq"

  check-command "git"
  check-command "unzip"
  check-command "pwsh" "powershell"  
  check-command "cspell"
  check-arm-ttk
  _msg "\n🧾 checking the package manifest"
  check-matching-playbook-declarations
  check-matching-workbook-declarations
  check-matching-analytic-rules-declarations
}

usage() {
  _msg "build_solution.sh"
  _msg ""
  _msg "Builds a Sentinel package for Solutions/Tanium"
  _msg ""
  _msg "Will build a Sentinel package using the manifest Solutions/Tanium/Data/Solution_Tanium.json via Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1"
  _msg ""
  _msg "The built package will land in Solutions/Tanium/Package"
  _msg ""
  exit 0
}

main() {
  (cd "$(git rev-parse --show-toplevel)" || _die "Unable to cd to top level repo directory"
    while :; do
      case "${1-}" in
      -h | --help) usage ;;
      -?*) _die "Unknown option: $1" ;;
      *) break ;;
      esac
      shift
    done

    _shout "Checking prerequisites"
    check_prerequisites

    _shout "Checking spelling errors"
    if ! check_spelling ; then
      _msg_error "Found 1 or more misspellings!"
      return 1
    fi
    
    _shout "Building Solution"
    build_solution
  )
}

main "$@"
