#!/usr/bin/env bash

set -Eeuo pipefail

# globals
_TOOL_DIRECTORY="Tools/Create-Azure-Sentinel-Solution/V2"
_SH_TOOL_DIRECTORY="./$_TOOL_DIRECTORY"
_INPUT_DIRECTORY="$_SH_TOOL_DIRECTORY/input"
_REBUILD=0

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

report_failure() {
  declare log=$1
  grep Failed "$log"
  grep -E 'Errors.*:.*[A-Z]' -A10 "$log" || true
}

build_solution() {
  _msg "🏗  Building Tanium Sentinel solution"
  pwsh -Command "$_TOOL_DIRECTORY/createSolutionV2.ps1"
}

build_failed() {
  grep -qm1 '^Failed' "$1"
}

report_success() {
  declare log=$1

  _msg_success "🎉  Build success"

  _msg <<END
  - files: ./Solutions/Tanium/Package/*
  - build log: $log"
END

  _msg "\nYou should next run Solutions/Tanium/check_build.sh to compare this build with the previous build"
}

clear_existing_build_inputs() {
  rm -f "$_INPUT_DIRECTORY"/*
}

copy_tanium_build_manifest_into_tooling() {
  cp ./Solutions/Tanium/Data/Solution_Tanium.json "$_INPUT_DIRECTORY/Solution_Tanium.json"
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
  _msg "🚮  Clearing existing inputs from the solution build tool"
  clear_existing_build_inputs
  _msg "💾  Copying Tanium build input into the solution build tool"
  copy_tanium_build_manifest_into_tooling
  _msg "🚛  Moving contents of Tanium/Package into a temporary location ($tmpdir) so they are not included in the zip"
  move_tanium_package_directory_to_temporary_location "$tmpdir"
}

post_build_cleanup() {
  local tmpdir=$1
  _msg "🚮  Clearing inputs from the solution build tool"
  rm -f "$_INPUT_DIRECTORY"/*
  _msg "🆗  Restoring original inputs in the solution build tool"
  git checkout "$_INPUT_DIRECTORY"
  _msg "⏪  Copying zip files from temporary location back into Tanium/Package"
  copy_previous_tanium_package_zip_files_from_temporary_location_back_into_package_directory "$tmpdir"
}

check-command() {
  if ! command -v "$1" >/dev/null; then
    _die "$1 command not found: please brew install ${2-:$1}"
  fi
}

check-new-version() {
  local declared_version
  declared_version=$(jq -r ".Version" Solutions/Tanium/Data/Solution_Tanium.json)
  DECLARED_VERSION=$declared_version

  if [[ "$_REBUILD" -eq 1 ]]; then
    rm "Solutions/Tanium/Package/$declared_version.zip" || true
  fi

  if find Solutions/Tanium/Package -name '*.zip' | grep -q "$declared_version"; then
    _msg
    _msg_error "Found $declared_version.zip already built in Solutions/Tanium/Package"
    _msg
    _msg "Did you forget to increment the version in Solutions/Tanium/Data/Solution_Tanium.json?"
    _msg "If you want to rebuild $declared_version then delete the zip file first or use --rebuild"
    _msg
    exit 1
  fi
}

check-matching-playbook-declarations() {
  local playbook_json_files
  local declared_playbook_json_files
  local undeclared_playbook_json_files
  local missing_playbook_json_files

  playbook_json_files=$(find Solutions/Tanium/Playbooks -name "azuredeploy.json" | sort | sed -e 's|Solutions/Tanium/||')
  declared_playbook_json_files=$(jq -r ".Playbooks[]" Solutions/Tanium/Data/Solution_Tanium.json | sort)

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
  check-command "jq"
  check-command "git"
  check-command "pwsh" "powershell"
  check-new-version
  check-matching-playbook-declarations
}

usage() {
  _msg "build_solution.sh to build Solutions/Tanium"
  _msg "Will build according to metadata from Solutions/Tanium/Data/Solution_Tanium.json"
  _msg "Use --rebuild to rebuild the same version again"
  exit 0
}

main() {
  (cd "$(git rev-parse --show-toplevel)" || _die "Unable to cd to top level repo directory"
    while :; do
      case "${1-}" in
      -h | --help) usage ;;
      -r | --rebuild) _REBUILD=1 ;;
      -?*) _die "Unknown option: $1" ;;
      *) break ;;
      esac
      shift
    done

    check-prerequisites
    _shout "Building Solutions/Tanium $DECLARED_VERSION using $_TOOL_DIRECTORY"
    declare logfile="/tmp/tanium_sentinel_create_package.log"
    declare tmpdir
    tmpdir=$(mktemp -d)
    pre_build_prep "$tmpdir"
    build_solution | tee /dev/tty > "$logfile"
    post_build_cleanup "$tmpdir"
    if build_failed "$logfile"; then
      report_failure "$logfile"
      _die "Detected a build failure"
    fi
    report_success "$logfile"
  )
}

main "$@"
