#!/usr/bin/env bash
# Manual API test script (Lab 4 + Lab 5 + Lab 6). Start the server first:
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

# check_fields <path[|alt]> <escalate> <confidence: number|null|0.0>  -> Lab 6 fields of the last /v1/chat BODY
check_fields() {
  local result
  result=$(printf '%s' "$BODY" | python -c '
import sys, json
want_path, want_esc, want_conf = sys.argv[1].split("|"), sys.argv[2] == "true", sys.argv[3]
try:
    b = json.load(sys.stdin)
except ValueError:
    print("body is not JSON"); sys.exit()
missing = [k for k in ("path", "escalate", "confidence") if k not in b]
if missing:
    print("missing " + ",".join(missing)); sys.exit()
path, esc, c = b["path"], b["escalate"], b["confidence"]
def conf_matches(w):
    if w == "null":
        return c is None
    if w == "number":
        return isinstance(c, (int, float)) and 0 <= c <= 1
    return c is not None and c == float(w)
ok = path in want_path and esc is want_esc and any(conf_matches(w) for w in want_conf.split("|"))
print(("OK" if ok else "MISMATCH") + f" path={path} escalate={str(esc).lower()} confidence={c}")
' "$1" "$2" "$3")
  echo "  fields: expected path=$1 escalate=$2 confidence=$3 -> $result"
  if [[ "$result" == OK* ]]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
}

run "health" 200 "$BASE_URL/health"
run "chat fee" 200 -X POST "$BASE_URL/v1/chat" "${PY_HDR[@]}" -d '{"message":"tuition for 18 credits and 2 retake","session_id":"demo"}'
REQUEST_ID=$(printf '%s' "$BODY" | json_get request_id)
echo "  request_id=$REQUEST_ID"
check_fields deterministic false null
run "chat rule with source" 200 -X POST "$BASE_URL/v1/chat" "${PY_HDR[@]}" -d '{"message":"can I register my thesis with 118 credits"}'
check_fields "llm|retrieval" false "number|null"
run "chat abstain (not in the documents)" 200 -X POST "$BASE_URL/v1/chat" "${PY_HDR[@]}" -d '{"message":"is there a scholarship for good students"}'
check_fields abstain true 0.0
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
