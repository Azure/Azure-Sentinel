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
  check-command "bat"
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

main() {
  check-prerequisites

  local previous
  local current

  (cd "$(top_level_repo_directory)" || _die "Unable to cd to top level repo directory"
    previous=$(previous_build_zip_file)
    current=$(current_build_zip_file)

    _msg ""
    _msg "Previous package: $previous"
    _msg "Current package: $current"
    _msg ""

    check_expected_files "$current"
    compare_contents "$previous" "$current"
  )
}

main "$@"
