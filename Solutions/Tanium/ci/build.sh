#!/usr/bin/env bash

###########################################
#  RESPONSE FUNCTIONS
###########################################
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
  _msg "  ✅ $1"
}

_shout() {
  _msg
  echo >&2 "$(tput bold)${*}$(tput sgr0)"
  _msg
}

_die() {
  local msg=$1
  local code=${2:-1} # default exit status 1 when $2 unset or empty
  _msg_error "😢  $msg"
  exit "${code:-1}"
}

###########################################
#  CONSTANTS
###########################################
_solution_folder_path="./Solutions/Tanium"
_solution_data_folder_path="./Solutions/Tanium/Data"
_package_folder_path="../Package"

###########################################
#  VALIDATION
###########################################
validate_arm_files(){
  _msg "💪 checking arm-ttk results"

  if ! pwsh ./run-arm-ttk-accurately.ps1 "Tanium"; then
    echo "ARM Validation failed"
    return 1
  else
      _msg_success "Passed!"
  fi
}

validate_json_files(){
  _msg "\n📄 checking package json file validation"

  if ! pwsh ./run-json-validation.ps1 "$_solution_folder_path"; then
    echo "JSON Validation failed"
    return 1
  else
    _msg_success "Passed!"
  fi
}

validate_build(){
  _msg "\n📦 checking package build result"

  build_solution

  current_published_version=$(pwsh ./get-published-version.ps1 "$_solution_data_folder_path")
  _msg "  🏷️  current published version is ${current_published_version}"

  built_version=$(pwsh ./get-new-version.ps1  "$_solution_data_folder_path")
  _msg "  🏷️  new publish version is ${built_version}"

  if [ "$current_published_version" == "$built_version" ]; then
    _msg_error "New version was not published! Did you forget to increment?"
    return 1
  fi
}

############################################
#  TOOLING FUNCTIONS
###########################################
check-command() {
  _msg "  🔧 checking $1"
  if ! command -v "$1" >/dev/null; then
    _die "$1 command not found: please brew install ${2-:$1}"
  fi
}

check-arm-ttk() {
  _msg "  🔧 checking arm-ttk module in powershell"
  if ! pwsh -c Get-Command Test-AzTemplate -ErrorAction SilentlyContinue | grep -q arm-ttk; then
    _die "arm-ttk module not found in your powershell"
  fi
}

###########################################
#  MANIFEST FUNCTIONS
###########################################
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
 
  actual_files=$(find "../${expected_folder}" -name "*.${expected_file_type}" ! -name connect-module-connections.json | sort | sed -e 's|../||')
  declared_files=$(jq -r "$json_property" ../Data/Solution_Tanium.json | sort)

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

############################################
#  COMMANDS
###########################################
check_spelling(){

  _shout "Checking spelling errors"

  # Change directories, because if you specify the directory to cspell it won't check recursively
  local current_dir
  current_dir=$(pwd)
  cd ..

  local error_file
  error_file="./ci/cspell-results.json"

  # Delete the current spell check file if it exists 
  [ -f "$error_file" ] && rm "$error_file"

  local error_count  
  if ! cspell --quiet . --exclude ./Workbooks/connect-module-connections.json --exclude ./Package/mainTemplate.json --reporter @cspell/cspell-json-reporter > "$error_file"; then
    error_count=$(jq '.issues | length' "$error_file")
    _msg_error "Found ${error_count} misspellings!"
      return 1
  else
    # Delete the results, since we passed
    [ -f "$error_file" ] && rm "$error_file"
    _msg_success "Passed!"
  fi  

  # Don't forget to go back to the original folder
  cd "$current_dir"
}

check_prerequisites() {
  _shout "Checking prerequisites"

  _msg "🧰 checking required tools are installed"
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

check_validations(){
  _shout "Running Validations"
  validate_arm_files
  validate_json_files
  validate_build
}

build_solution() {
  local repo_root
  repo_root=$(git rev-parse --show-toplevel)
  pwsh ./build-silently.ps1 "$_solution_data_folder_path" || _die "build-silently.ps1 failed"
  _msg_success "Build finished"
}

deploy_to_azure(){
  local resource_group=$1
  local workspace=$2
  local region=$3
  local version=$4
  local build_number
  build_number=$(bash -c 'echo $RANDOM')

  _shout "Deploying"

  _msg "\n🚀 deploying to azure for review"

  # TODO Now push up the templates to the demo/qa environment for review
  if ( ! az deployment group create \
    --resource-group "$resource_group" \
    --name "${version}-Preview${build_number}"  \
    --template-file "${_package_folder_path}/mainTemplate.json" \
    --parameters workspace-location="${region}" \
    --parameters workspace="${workspace}" \
    --parameters workbook1-name="Tanium Workbook v${version}" \
    --output none ) then
      _msg_error "Deployment failed! Check resource group activity for details."
      return 1
  else 
    _msg_success "Deployment completed!"
  fi

  _msg_warning "\n⚠️  Please verify all the template data in the the workspace ${workspace} and complete any final QA tasks."
}