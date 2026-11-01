"""Rate limiter for the web API (Bonus +1).

Owner: Gia Huy.
"""

import time


class RateLimiter:
    """Simple in-memory sliding-window rate limiter per client."""

    def __init__(self, max_requests: int = 10, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._history: dict[str, list[float]] = {}

    def allow(self, client: str) -> bool:
        """Return True if the client is within quota; False if rate-limited."""
        now = time.monotonic()
        history = self._history.setdefault(client, [])
        cutoff = now - self.window_seconds
        self._history[client] = [t for t in history if t > cutoff]
        if len(self._history[client]) >= self.max_requests:
            return False
        self._history[client].append(now)
        return True
