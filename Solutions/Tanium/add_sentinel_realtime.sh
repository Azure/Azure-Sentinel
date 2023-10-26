#!/usr/bin/env bash

# https://betterdev.blog/minimal-safe-bash-script-template/

set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

script_name=$(basename "${BASH_SOURCE[0]}")

usage() {
  cat <<EOF
Usage: $script_name [-h] -r sentinel-realtime-path -p sentinel-package-path

This script adds Sentinel Realtime to a given Sentinel solution Package files.

- steps and outputs are added to createUiDefinition.json
- parameters and resources are added to mainTemplate.json
- both files are replaced in the latest package zip file

For example:

Given a Package directory

Package
├── 1.0.4.zip
├── 1.0.9.zip
├── 1.0.10.zip
├── 2.0.0.zip
├── 2.0.1.zip
├── 3.0.0.zip
├── createUiDefinition.json
└── mainTemplate.json

And a run of this script

    $ ./$script_name -r ~/ghe/stephen-ball/microsoft-integrations/sentinel-realtime -p ./Package

Then

- Package/createUiDefinition.json would be updated with Sentinel Realtime
- Package/mainTemplate.json would be updated with Sentinel Realtime
- Package/3.0.0.zip would be updated with those new files

Required parameters:

-r, --realtime-path   Path to Sentinel Realtime
-p, --package-path    Path to the Tanium solution Package directory

Other options:

-h, --help            Print this help and exit
-v, --verbose         Be verbose
--no-color            No colors in output


EOF
  exit
}

cleanup() {
  trap - SIGINT SIGTERM ERR EXIT
  # script cleanup here
}

setup_colors() {
  if [[ -t 2 ]] && [[ -z "${NO_COLOR-}" ]] && [[ "${TERM-}" != "dumb" ]]; then
    NOFORMAT='\033[0m' RED='\033[0;31m' GREEN='\033[0;32m' ORANGE='\033[0;33m' BLUE='\033[0;34m' PURPLE='\033[0;35m' CYAN='\033[0;36m' YELLOW='\033[1;33m'
  else
    NOFORMAT='' RED='' GREEN='' ORANGE='' BLUE='' PURPLE='' CYAN='' YELLOW=''
  fi
}

msg() {
  echo >&2 -e "${1-}"
}

die() {
  local msg=$1
  local code=${2-1} # default exit status 1
  msg "$msg"
  exit "$code"
}

parse_params() {
  realtime=''
  package=''
  
  while :; do
    case "${1-}" in
    -h | --help) usage ;;
    -v | --verbose) set -x ;;
    --no-color) NO_COLOR=1 ;;
    -r | --realtime-path)
      realtime="${2-}"
      shift
      ;;
    -p | --package-path) # example named parameter
      package="${2-}"
      shift
      ;;
    -?*) die "Unknown option: $1" ;;
    *) break ;;
    esac
    shift
  done

  # check required params and arguments
  [[ -z "${realtime-}" ]] && die "Missing required parameter: --realtime-path"
  [[ -z "${package-}" ]] && die "Missing required parameter: --package-path"

  return 0
}

parse_params "$@"
setup_colors

# script logic here

current_build_zip_file() {
  find "$package" -name '*.zip' | sort -V | tail -1
}

if [[ -n "$NOFORMAT" ]]; then
  msg "Ooo ${RED}C${GREEN}O${BLUE}L${ORANGE}O${PURPLE}R${CYAN}S${YELLOW}!${NOFORMAT}"
  msg ""
fi

msg "${ORANGE}Read parameters:${NOFORMAT}"
msg "-realtime-path: ${realtime}"
msg "-package-path: ${package}"
msg ""
msg "${ORANGE}Checking expectations:${NOFORMAT}"

realtimeTemplate="${realtime}/mainTemplate.json"
realtimeUi="${realtime}/createUiDefinition.json"
packageTemplate="${package}/mainTemplate.json"
packageUi="${package}/createUiDefinition.json"
tempTemplate=$(mktemp)
tempUi=$(mktemp)
zip=$(current_build_zip_file)

if [[ -f "$realtimeTemplate" ]]; then
  msg "  ${GREEN}Found ${YELLOW}mainTemplate.json${GREEN} in realtime-path${NOFORMAT}"
else
  die "  ${RED}Did not find mainTemplate.json in realtime-path${NOFORMAT}"
fi

if [[ -f "$realtimeUi" ]]; then
  msg "  ${GREEN}Found ${YELLOW}createUiDefinition.json${GREEN} in realtime-path${NOFORMAT}"
else
  die "  ${RED}Did not find createUiDefinition.json in realtime-path${NOFORMAT}"
fi

if [[ -f "$packageTemplate" ]]; then
  msg "  ${GREEN}Found ${YELLOW}mainTemplate.json${GREEN} in package-path${NOFORMAT}"
else
  die "  ${RED}Did not find mainTemplate.json in package-path${NOFORMAT}"
fi

if [[ -f "$packageUi" ]]; then
  msg "  ${GREEN}Found ${YELLOW}createUiDefinition.json${GREEN} in package-path${NOFORMAT}"
else
  die "  ${RED}Did not find createUiDefinition.json in package-path${NOFORMAT}"
fi

if [[ -f "$zip" ]]; then
  msg "  ${GREEN}Identified ${CYAN}$zip${GREEN} as the latest package zip in package-path${NOFORMAT}"
else
  die "  ${RED}Did not find a package zip file in package-path${NOFORMAT}"
fi

msg ""
msg "${ORANGE}Adding Sentinel Realtime to UI definition${NOFORMAT}"

if node add-sentinel-realtime-create-ui-definition.js "$realtimeUi" "$packageUi" > "$tempUi"; then
  msg "  ${GREEN}Added Sentinel Realtime to ${CYAN}$packageUi${NOFORMAT}"
  mv "$tempUi" "$packageUi"
else
  die "  ${RED}Error adding Sentinel Realtime to the package UI definition${NOFORMAT}"
fi

msg ""
msg "${ORANGE}Adding Sentinel Realtime to template definition${NOFORMAT}"

if node add-sentinel-realtime-main-template.js "$realtimeTemplate" "$packageTemplate" > "$tempTemplate"; then
  msg "  ${GREEN}Added Sentinel Realtime to ${CYAN}$packageTemplate${NOFORMAT}"
  mv "$tempTemplate" "$packageTemplate"
else
  die "  ${RED}Error adding Sentinel Realtime to the package template${NOFORMAT}"
fi

msg ""
msg "${ORANGE}Updating ${zip} with the new UI and template files${NOFORMAT}"
zipDirectory=$(dirname "$zip")
zipFile=$(basename "$zip")
if (cd "$zipDirectory"; zip -f "$zipFile"); then
  msg "  ${GREEN}Updated ${CYAN}${zip}${GREEN} with the Sentinel Realtime updated files${NOFORMAT}"
else
  die "  ${RED}Error adding Sentinel Realtime updated files to ${CYAN}${zip}${NOFORMAT}"
fi


msg ""
msg "${GREEN}Success!${NOFORMAT}"