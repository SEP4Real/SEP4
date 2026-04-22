#!/usr/bin/env bash
set -euo pipefail

LOCAL_BASE="${LOCAL_BASE:-http://localhost:8000}"
DEPLOYED_BASE="${DEPLOYED_BASE:-https://sep4.edproduction.dev}"

check() {
  local label="$1"
  local url="$2"
  echo "== $label"
  curl -fsS "$url"
  echo
}

check "Local /" "$LOCAL_BASE/"
check "Local /db-check" "$LOCAL_BASE/db-check"
check "Deployed /" "$DEPLOYED_BASE/"
check "Deployed /db-check" "$DEPLOYED_BASE/db-check"

echo "All smoke checks passed."
