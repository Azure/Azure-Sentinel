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
  echo >&2 "$(tput bold)${*}$(tput sgr0)"
}

_die() {
  local msg=$1
  local code=${2-1} # default exit status 1
  _msg_error "😢  $msg"
  exit "$code"
}

check-command() {
  if ! command -v "$1" >/dev/null; then
    _die "$1 command not found: please brew install ${2-:$1}"
  fi
}

check-prerequisites() {
  check-command "git"
  check-command "unzip"
}

top_level_repo_directory() {
  git rev-parse --show-toplevel
}

previous_build_zip_file() {
  find Solutions/Tanium/Package -name '*.zip' | sort -V | tail -2 | head -1
}

current_build_zip_file() {
  find Solutions/Tanium/Package -name '*.zip' | sort -V | tail -1
}

check_expected_files() {
  _msg ""
  if unzip -t "$1" "mainTemplate.json"; then
    _msg_success "✅  mainTemplate.json"
  fi

  _msg ""
  if unzip -t "$1" "createUiDefinition.json"; then
    _msg_success "✅  createUiDefinition.json"
  fi
}

compare_contents() {
  _msg "\nPrevious contents"
  unzip -l "$1" | sed -e 's/^/  /'

  _msg "\nCurrent contents"
  unzip -l "$2" | sed -e 's/^/  /'
}

show_diff_commands() {
  _msg "\nTo diff mainTemplate.json:"
  _msg "    check_build.sh diff mainTemplate.json"
  _msg "\nTo diff createUiDefinition.json:"
  _msg "    check_build.sh diff createUiDefinition.json"
}

show_manual_check_steps() {
  _msg ''
  _msg 'Next, you should manually check the createUiDefinition.json file and the mainTemplate.json file'
  _msg ''
  _msg '
  1. Validate createUiDefinition.json:

    • Open CreateUISandbox https://portal.azure.com/#blade/Microsoft_Azure_CreateUIDef/SandboxBlade.
    • Copy json content from createUiDefinition.json (in the recent version).
    • Clear that content in the editor and replace with copied content in step #2.
    • Click on preview
    • You should see the User Interface preview of data connector, workbook, etc., and descriptions you provided in
    input file.
    • Check the description and User Interface of solution preview.

  2. Validate maintemplate.json:

    Validate mainTemplate.json  by deploying the template in portal. Follow these steps to deploy in portal:

    • Open up https://aka.ms/AzureSentinelPrP which launches the Azure portal with the needed private preview flags.
    • Go to "Deploy a Custom Template" on the portal
    • Select "Build your own template in Editor".
    • Copy json content from mainTemplate.json  (in the recent version).
    • Clear that content in the editor and replace with copied content in step #3.
    • Click Save and then progress to selecting subscription, Sentinel-enabled resource group, and corresponding
    workspace, etc., to complete the deployment.
    • Click Review + Create to trigger deployment.
    • Check if the deployment successfully completes.
    • You should see the data connector, workbook, etc., deployed in the respective galleries and validate

    You can also validate individual playbooks by pasting their azuredeploy.json files into the "own template" editor.
  '
}

diff-within-zip() {
  local previous=$1
  local current=$2
  local file=$3
  diff -u <(unzip -p "$previous" "$file" | jq .) <(unzip -p "$current" "$file" | jq .)
}

main() {
  check-prerequisites

  local previous
  local current
  local command
  command=${1:-summary}

  (cd "$(top_level_repo_directory)" || _die "Unable to cd to top level repo directory"
    previous=$(previous_build_zip_file)
    current=$(current_build_zip_file)

    case "$command" in
      summary)
        _msg ""
        _msg "Previous package: $previous"
        _msg "Current package: $current"
        _msg ""

        check_expected_files "$current"
        compare_contents "$previous" "$current"
        show_diff_commands "$previous" "$current"
        show_manual_check_steps
        ;;
      diff)
        file=$2
        diff-within-zip "$previous" "$current" "$file"
        ;;
    esac
  )
}

main "$@"
