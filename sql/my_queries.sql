-- Lab 5 Part F (Gia Huy / wiih0521, issue #32).
-- Run on a fresh database from the repository root:
--   python scripts/migrate.py assistant.db
--   python scripts/seed.py assistant.db 300
-- seed.py appends data: do not seed the same database twice for these results.
-- Results below use 300 synthetic interactions (random seed 7).

-- F1: requests per intent, most frequent first.
SELECT intent, COUNT(*) AS requests
FROM interaction
GROUP BY intent
ORDER BY requests DESC, intent ASC;
-- intent   | requests
-- rule     | 140
-- fee      | 61
-- office   | 47
-- greeting | 26
-- unknown  | 26

-- F2: average latency in milliseconds per intent (one decimal place).
SELECT intent, ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY avg_latency_ms DESC, intent ASC;
-- intent   | avg_latency_ms
-- rule     | 76.2
-- unknown  | 8.1
-- fee      | 5.1
-- office   | 3.4
-- greeting | 2.4

-- F3: topics ranked by number of thumbs-down feedback entries.
-- Exclude NULL topics: greeting/fee/office/unknown have no handbook topic.
-- Count feedback entries, not distinct requests (the API allows repeat feedback).
-- Return the full ranking so ties and other topics remain visible.
SELECT i.topic, COUNT(*) AS thumbs_down
FROM interaction AS i
JOIN feedback AS f ON f.request_id = i.request_id
WHERE f.rating = -1 AND i.topic IS NOT NULL
GROUP BY i.topic
ORDER BY thumbs_down DESC, i.topic ASC;
-- topic   | thumbs_down
-- H26-4.2 | 8
-- H26-5.3 | 8
-- H26-7.2 | 2
-- H26-4.2 and H26-5.3 tie for the most thumbs-down.
-- Another 17 negative feedback entries have NULL topic and are excluded above.
