# curl_tests.sh output (Hai, 2026-11-06)

Command: API_ADMIN_KEY=change-me bash api-tests/curl_tests.sh (server: uvicorn assistant_api.main:create_app --factory)

```

== health (expect 200)
{"status":"ok","version":"1.0.0"}  [200]

== chat fee (expect 200)
{"answer":"Your tuition is 9,450,000 VND.","intent":"fee","sources":[],"degraded":false,"request_id":"7460ff56446a"}  [200]

== chat rule with source (200)
{"answer":"Based on 'Thesis registration': Students may register a thesis when they have at least 120 accumulated credits and a GPA of at least 2.0.","intent":"rule","sources":[{"id":"H26-5.3","title":"Thesis registration"}],"degraded":false,"request_id":"41e295900aeb"}  [200]

== chat empty (expect 422)
{"error":{"code":"invalid_request","message":"message: String should have at least 1 character"}}  [422]

== chat wrong type (expect 422)
{"error":{"code":"invalid_request","message":"message: Input should be a valid string"}}  [422]

== feedback (expect 201)
{"request_id":"abc123","rating":1,"comment":"clear answer","id":1,"created_at":"2026-11-06T13:49:00.837954Z"}  [201]

== feedback bad rating (422)
{"error":{"code":"invalid_request","message":"rating: Input should be less than or equal to 1"}}  [422]

== list feedback no key (401)
{"error":{"code":"missing_or_invalid_api_key","message":"Missing or invalid API key"}}  [401]

== list feedback with key (200)
[{"request_id":"abc123","rating":1,"comment":"clear answer","id":1,"created_at":"2026-11-06T13:49:00.837954Z"}]  [200]

== weather (200, or 503 if down)
{"temperature_c":28.7,"wind_kmh":5.2,"description":"clear sky","observed_at":"2026-11-06T13:45","stale":false}  [200]

== unknown route (404)
{"error":{"code":"not_found","message":"Not Found"}}  [404]
```
