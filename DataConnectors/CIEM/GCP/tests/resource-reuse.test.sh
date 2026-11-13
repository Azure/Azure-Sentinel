#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$(mktemp -d)"
trap 'rm -f -- "$TEST_DIR/gcloud" "$TEST_DIR/calls" "$TEST_DIR/stdout" "$TEST_DIR/stderr"; rmdir -- "$TEST_DIR"' EXIT

cat >"$TEST_DIR/gcloud" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$*" >>"$MOCK_CALLS"

if [[ "$MOCK_SCENARIO" == new ]]; then
  for resource in 'pubsub topics' 'pubsub subscriptions' 'logging sinks'; do
    if [[ "$*" == "$resource describe "* ]] && ! grep -q "^$resource create " "$MOCK_CALLS"; then
      echo 'ERROR: NOT_FOUND: simulated missing resource' >&2
      exit 1
    fi
  done
fi

fail_read() {
  echo 'ERROR: PERMISSION_DENIED: simulated resource-read failure' >&2
  exit 42
}

case "$*" in
  "pubsub topics list "*)
    [[ "$*" == *"--filter=name=projects/$PROJECT_ID/topics/UCC-ControlPlane-Topic"* ]] || exit 97
    [[ "$MOCK_SCENARIO" != topic-list-failure ]] || fail_read
    [[ "$MOCK_SCENARIO" == new ]] || echo "projects/$PROJECT_ID/topics/UCC-ControlPlane-Topic"
    ;;
  "pubsub subscriptions list "*)
    [[ "$*" == *"--filter=name=projects/$PROJECT_ID/subscriptions/$SUBSCRIPTION_NAME"* ]] || exit 97
    [[ "$MOCK_SCENARIO" != subscription-list-failure ]] || fail_read
    [[ "$MOCK_SCENARIO" == new ]] || echo "projects/$PROJECT_ID/subscriptions/$SUBSCRIPTION_NAME"
    ;;
  "logging sinks list "*)
    [[ "$*" == *"--filter=name=UCC-ControlPlane-Sink"* ]] || exit 97
    [[ "$MOCK_SCENARIO" != sink-list-failure ]] || fail_read
    [[ "$MOCK_SCENARIO" == new ]] || echo 'UCC-ControlPlane-Sink'
    ;;
  "pubsub subscriptions describe "*)
    [[ "$MOCK_SCENARIO" != subscription-read-failure ]] || fail_read
    case "$MOCK_SCENARIO" in
      wrong-topic) echo "projects/$PROJECT_ID/topics/unrelated-topic" ;;
      empty-topic) ;;
      deleted-topic) echo '_deleted-topic_' ;;
      byo) echo "projects/$PROJECT_ID/topics/customer-audit-topic" ;;
      *) echo "projects/$PROJECT_ID/topics/UCC-ControlPlane-Topic" ;;
    esac
    ;;
  "pubsub topics describe "*)
    [[ "$MOCK_SCENARIO" != topic-read-failure ]] || fail_read
    echo "projects/$PROJECT_ID/topics/customer-audit-topic"
    ;;
  "logging sinks describe "*)
    case "$*" in
      *"--format=value(destination)"*)
        [[ "$MOCK_SCENARIO" != sink-read-failure ]] || fail_read
        if [[ "$MOCK_SCENARIO" == empty-destination ]]; then
          :
        elif [[ "$MOCK_SCENARIO" == wrong-destination ]]; then
          echo "pubsub.googleapis.com/projects/$PROJECT_ID/topics/unrelated-topic"
        else
          echo "pubsub.googleapis.com/projects/$PROJECT_ID/topics/UCC-ControlPlane-Topic"
        fi
        ;;
      *"--format=value(filter)"*)
        [[ "$MOCK_SCENARIO" != filter-read-failure ]] || fail_read
        if [[ "$MOCK_SCENARIO" == empty-filter ]]; then
          :
        elif [[ "$MOCK_SCENARIO" == wrong-filter ]]; then
          echo 'severity>=ERROR'
        else
          echo 'logName:"cloudaudit.googleapis.com"'
        fi
        ;;
      *"--format=value(writerIdentity)"*) echo 'serviceAccount:sink@example.invalid' ;;
    esac
    ;;
  "config set project "* | "services enable "* | \
  "iam workload-identity-pools "* | "iam service-accounts "* | "iam roles "* | \
  "projects add-iam-policy-binding "* | \
  "pubsub topics create "* | "pubsub subscriptions create "* | \
  "pubsub topics add-iam-policy-binding "* | "pubsub subscriptions add-iam-policy-binding "* | \
  "logging sinks create "*)
    ;;
  *)
    echo "Unexpected mock command: $*" >&2
    exit 97
    ;;
esac
exit 0
MOCK
chmod +x "$TEST_DIR/gcloud"

failures=0
cases=0
run_case() {
  local script="$1" scenario="$2" expected="$3" message="${4:-}" status
  : >"$TEST_DIR/calls"
  if PATH="$TEST_DIR:$PATH" \
      PROJECT_ID='fixture-project' PROJECT_NUMBER='123456789012' \
      TENANT_ID='00000000-0000-0000-0000-000000000001' \
      WORKLOAD_IDENTITY_PROVIDER_ID='fixture-provider' \
      SERVICE_ACCOUNT_EMAIL='collector@fixture-project.iam.gserviceaccount.com' \
      SUBSCRIPTION_NAME='fixture-sub' MOCK_SCENARIO="$scenario" MOCK_CALLS="$TEST_DIR/calls" \
      bash "$SCRIPT_DIR/$script" >"$TEST_DIR/stdout" 2>"$TEST_DIR/stderr"; then
    status=0
  else
    status=$?
  fi

  cases=$((cases + 1))
  local passed=true
  if [[ "$expected" == success ]]; then
    [[ "$status" == 0 ]] && grep -q 'configured' "$TEST_DIR/stdout" || passed=false
    if [[ "$scenario" == new ]]; then
      grep -q '^pubsub topics create ' "$TEST_DIR/calls" || passed=false
      grep -q '^pubsub subscriptions create ' "$TEST_DIR/calls" || passed=false
      grep -q '^logging sinks create ' "$TEST_DIR/calls" || passed=false
    elif grep -Eq '^(pubsub (topics|subscriptions)|logging sinks) (create|update|delete) ' "$TEST_DIR/calls"; then
      passed=false
    fi
  else
    [[ "$status" != 0 ]] && grep -Fq "$message" "$TEST_DIR/stderr" || passed=false
    if grep -q 'configured' "$TEST_DIR/stdout" ||
        grep -Eq '^(iam |projects add-iam-policy-binding |pubsub .* (create|update|delete|add-iam-policy-binding) |logging sinks (create|update|delete) )' "$TEST_DIR/calls"; then
      passed=false
    fi
  fi

  if "$passed"; then
    printf 'PASS: %s / %s\n' "$script" "$scenario"
  else
    printf 'FAIL: %s / %s (exit %s)\n' "$script" "$scenario" "$status" >&2
    cat "$TEST_DIR/stdout" "$TEST_DIR/stderr" >&2
    failures=$((failures + 1))
  fi
}

provision='provision-pubsub-and-sink.sh'
run_case "$provision" matching success
run_case "$provision" new success
run_case "$provision" wrong-topic failure "expected topic 'projects/fixture-project/topics/UCC-ControlPlane-Topic'"
run_case "$provision" empty-topic failure "expected topic"
run_case "$provision" wrong-destination failure "expected destination 'pubsub.googleapis.com/projects/fixture-project/topics/UCC-ControlPlane-Topic'"
run_case "$provision" empty-destination failure "expected destination"
run_case "$provision" wrong-filter failure "expected filter 'logName:\"cloudaudit.googleapis.com\"'"
run_case "$provision" empty-filter failure "expected filter"
run_case "$provision" topic-list-failure failure "Cannot inspect Pub/Sub topic"
run_case "$provision" subscription-list-failure failure "Cannot inspect Pub/Sub subscription"
run_case "$provision" sink-list-failure failure "Cannot inspect logging sink"
run_case "$provision" subscription-read-failure failure "Cannot read Pub/Sub subscription"
run_case "$provision" sink-read-failure failure "Cannot read logging sink"
run_case "$provision" filter-read-failure failure "Cannot read logging sink"

existing='existing-pubsub-and-sink.sh'
run_case "$existing" byo success
run_case "$existing" empty-topic failure "has no readable topic"
run_case "$existing" deleted-topic failure "has no readable topic"
run_case "$existing" subscription-read-failure failure "Cannot read Pub/Sub subscription"
run_case "$existing" topic-read-failure failure "Cannot read Pub/Sub topic"

printf '\n%s cases; %s failed.\n' "$cases" "$failures"
[[ "$failures" == 0 ]]
