#!/usr/bin/env python3
"""Pi-hole v6 API client."""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path


class PiHoleClient:
    def __init__(self, base_url, password=None, sid=None, token=None):
        self.base_url = base_url.rstrip("/")
        self.password = password
        self.sid = sid
        self.token = token
        self._session_valid_until = 0

    def _request(self, path, method="GET", body=None, auth=True):
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}
        if auth:
            if not self.sid:
                self._auth()
            headers["X-FTL-SID"] = self.sid
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8")
            raise RuntimeError(f"Pi-hole API error {e.code}: {text}") from e

    def _auth(self):
        if not self.password:
            raise RuntimeError("No Pi-hole password configured")
        body = {"password": self.password}
        resp = self._request("/api/auth", method="POST", body=body, auth=False)
        if "session" not in resp:
            raise RuntimeError(f"Auth failed: {resp}")
        self.sid = resp["session"]["sid"]
        # Default Pi-hole v6 sessions last 30 minutes; refresh early
        self._session_valid_until = time.time() + 1500

    def get_summary(self):
        """Fetch summary stats from Pi-hole v6."""
        return self._request("/api/stats/summary")

    def get_top_items(self, count=5):
        return self._request(f"/api/stats/top_items?count={count}")


def load_password(path=None):
    if path is None:
        path = Path.home() / "eink-pihole" / ".pihole_pass"
    p = Path(path)
    if not p.exists():
        return None
    return p.read_text().strip()


def main():
    base = os.environ.get("PIHOLE_URL", "http://127.0.0.1")
    pw = load_password()
    if not pw:
        print("No password found. Set it in ~/eink-pihole/.pihole_pass", file=sys.stderr)
        sys.exit(1)
    client = PiHoleClient(base, password=pw)
    summary = client.get_summary()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
