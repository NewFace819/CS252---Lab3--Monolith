#!/usr/bin/env bash
# Manual API test script (Lab 4 + Lab 5). Start the server first:
#   uvicorn assistant_api.main:create_app --factory --reload
# Configure with env vars:
#   BASE_URL       server address (default http://127.0.0.1:8000; BASE is still accepted)
#   API_ADMIN_KEY  admin key, must match the server's API_ADMIN_KEY (default change-me)
# Needs only curl and python (no jq).
set -u
BASE_URL="${BASE_URL:-${BASE:-http://127.0.0.1:8000}}"
ADMIN="${API_ADMIN_KEY:-change-me}"
PASS=0; FAIL=0
hr() { echo; echo "== $1"; }

# run <label> <expected-status[|alt]> <curl args...>  -> prints body, expected vs actual; sets BODY
run() {
  local label="$1" expected="$2"; shift 2
  hr "$label (expect $expected)"
  local out; out=$(curl -s -w $'\n%{http_code}' "$@")
  local actual="${out##*$'\n'}"; BODY="${out%$'\n'*}"
  echo "$BODY"
  if [[ "|$expected|" == *"|$actual|"* ]]; then PASS=$((PASS+1)); echo "  expected=$expected actual=$actual  OK"
  else FAIL=$((FAIL+1)); echo "  expected=$expected actual=$actual  MISMATCH"; fi
}
json_get() { python -c 'import sys,json; print(json.load(sys.stdin).get(sys.argv[1],""))' "$1"; }
PY_HDR=(-H "Content-Type: application/json")

run "health" 200 "$BASE_URL/health"
run "chat fee" 200 -X POST "$BASE_URL/v1/chat" "${PY_HDR[@]}" -d '{"message":"tuition for 18 credits and 2 retake","session_id":"demo"}'
REQUEST_ID=$(printf '%s' "$BODY" | json_get request_id)
echo "  request_id=$REQUEST_ID"
run "chat rule with source" 200 -X POST "$BASE_URL/v1/chat" "${PY_HDR[@]}" -d '{"message":"can I register my thesis with 118 credits"}'
run "chat empty" 422 -X POST "$BASE_URL/v1/chat" "${PY_HDR[@]}" -d '{"message":""}'
run "chat wrong type" 422 -X POST "$BASE_URL/v1/chat" "${PY_HDR[@]}" -d '{"message":123}'
run "feedback for real request_id" 201 -X POST "$BASE_URL/v1/feedback" "${PY_HDR[@]}" -d "{\"request_id\":\"$REQUEST_ID\",\"rating\":1,\"comment\":\"clear answer\"}"
run "feedback unknown request_id 'nope'" 404 -X POST "$BASE_URL/v1/feedback" "${PY_HDR[@]}" -d '{"request_id":"nope","rating":1}'
run "feedback bad rating" 422 -X POST "$BASE_URL/v1/feedback" "${PY_HDR[@]}" -d "{\"request_id\":\"$REQUEST_ID\",\"rating\":7}"
run "list feedback no key" 401 "$BASE_URL/v1/feedback"
run "list feedback with key" 200 -H "X-API-Key: $ADMIN" "$BASE_URL/v1/feedback"
run "stats intents no key" 401 "$BASE_URL/v1/stats/intents"
run "stats intents with key" 200 -H "X-API-Key: $ADMIN" "$BASE_URL/v1/stats/intents"
run "weather (200, or 503 if upstream down)" "200|503" -m 10 "$BASE_URL/v1/weather"
run "unknown route" 404 "$BASE_URL/v1/nope"

echo; echo "== summary: $PASS matched, $FAIL mismatched"
[ "$FAIL" -eq 0 ]
