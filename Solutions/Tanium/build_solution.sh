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

build_solution() {
  _msg "🤖 Sorry but the V3 build script requires user interaction"
  _msg ""
  _msg "Run this command to perform the build:"
  _msg ""
  _msg "    (cd ../.. && pwsh ./Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1)"
  _msg ""
  _msg "At the prompt type in: ./Solutions/Tanium/Data"
  _msg ""
  _msg "e.g. Enter solution data file path : ./Solutions/Tanium/Data"
  _msg ""
  _msg "---"
  _msg "NOTE: Property: \"id\" must use one of the following expressions for an resourceId property is an IGNORABLE error"
  _msg "Citation: https://github.com/Azure/Azure-Sentinel/tree/e92286da7d185c99c6d30c2cb8c86bbeca1a99ba/Tools/Create-Azure-Sentinel-Solution/V3#arm-ttk-failue-for-contentproductid-id-issues"
  _msg ""
}

move_tanium_package_directory_to_temporary_location() {
  local tmpdir=$1

  mv "./Solutions/Tanium/Package" "$tmpdir/"
  mkdir -p "./Solutions/Tanium/Package"
}

copy_previous_tanium_package_zip_files_from_temporary_location_back_into_package_directory() {
  local tmpdir=$1
  find "$tmpdir/Package" -name '*.zip' -exec cp "{}" ./Solutions/Tanium/Package \;
}

pre_build_prep() {
  local tmpdir=$1
  _msg "🚛  Moving contents of Tanium/Package into a temporary location ($tmpdir) so they are not included in the zip"
  move_tanium_package_directory_to_temporary_location "$tmpdir"
}

post_build_cleanup() {
  local tmpdir=$1
  _msg "⏪  Copying zip files from temporary location back into Tanium/Package"
  copy_previous_tanium_package_zip_files_from_temporary_location_back_into_package_directory "$tmpdir"
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

check-matching-playbook-declarations() {
  local playbook_json_files
  local declared_playbook_json_files
  local undeclared_playbook_json_files
  local missing_playbook_json_files

  playbook_json_files=$(find Solutions/Tanium/Playbooks -name "azuredeploy.json" | sort | sed -e 's|Solutions/Tanium/||')
  declared_playbook_json_files=$(jq -r ".Playbooks[]" Solutions/Tanium/Data/Solution_Tanium.json | sort)

  _msg "  🕵️  checking that playbook json files are all declared in the manifest"
  # comm -23 : omit lines in common and lines only in the second file
  undeclared_playbook_json_files=$(comm -23 <(echo "$playbook_json_files") <(echo "$declared_playbook_json_files"))
  if [[ -n "$undeclared_playbook_json_files" ]]; then
    _msg_error "Found undeclared playbook json files:"
    _msg "$undeclared_playbook_json_files"
    _msg
    _msg "Did you forget to add them to Solutions/Tanium/Data/Solution_Tanium.json?"
    _msg
    exit 1
  fi

  _msg "  🕵️  checking that all playbooks declared in the manifest have playbook json files"
  # comm -13 : omit lines in common and lines only in the first file
  missing_playbook_json_files=$(comm -13 <(echo "$playbook_json_files") <(echo "$declared_playbook_json_files"))
  if [[ -n "$missing_playbook_json_files" ]]; then
    _msg_error "Found declared playbook json files in Data/Solution_Tanium.json but missing the actual file:"
    _msg "$missing_playbook_json_files"
    _msg
    _msg "Did you forget to add them to Solutions/Tanium/Playbooks?"
    _msg
    exit 1
  fi
}

check-prerequisites() {
  _msg "🧰 checking prerequisites"
  check-command "jq"
  check-command "git"
  check-command "pwsh" "powershell"
  check-arm-ttk
  _msg "🧾 checking the package manifest"
  check-matching-playbook-declarations
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
    check-prerequisites
    _shout "Building Solution"
    build_solution
  )
}

main "$@"
