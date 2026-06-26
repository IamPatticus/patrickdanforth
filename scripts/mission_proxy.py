#!/usr/bin/env python3
"""Reverse proxy: /mission/ -> chaotic-sanctum-site, everything else -> Control UI"""
import os, sys, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

MISSION_ROOT = os.path.expanduser("~/.openclaw/workspace/tmp/mission-control")
CONTROL_UI = "http://127.0.0.1:18790"
PORT = int(os.environ.get("PROXY_PORT", 18789))

class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Suppress noisy logs
        pass

    def send_file(self, path, status=200):
        try:
            with open(path, "rb") as f:
                data = f.read()
            ct = "text/html"
            if path.endswith(".css"): ct = "text/css"
            elif path.endswith(".js"): ct = "application/javascript"
            elif path.endswith(".png"): ct = "image/png"
            elif path.endswith(".jpg") or path.endswith(".jpeg"): ct = "image/jpeg"
            elif path.endswith(".svg"): ct = "image/svg+xml"
            self.send_response(status)
            self.send_header("Content-Type", ct)
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_error(404)

    def proxy_control_ui(self):
        try:
            req = urllib.request.Request(
                CONTROL_UI + self.path,
                headers={"Host": "127.0.0.1:18789"},
                method=self.command,
            )
            resp = urllib.request.urlopen(req, timeout=10)
            self.send_response(resp.status)
            for k, v in resp.headers.items():
                if k.lower() not in ("transfer-encoding", "content-length"):
                    self.send_header(k, v)
            data = resp.read()
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(502, message=str(e))

    def do_GET(self):
        if self.path.startswith("/mission/"):
            rel = self.path[len("/mission/"):]
            if not rel or rel.endswith("/"):
                rel = rel.rstrip("/") + "/index.html" if rel else "index.html"
            fpath = os.path.join(MISSION_ROOT, rel.lstrip("/"))
            # Security: prevent escaping MISSION_ROOT
            real_fpath = os.path.realpath(fpath)
            real_root = os.path.realpath(MISSION_ROOT)
            if not real_fpath.startswith(real_root + os.sep) and real_fpath != real_root:
                self.send_error(403)
                return
            self.send_file(real_fpath)
        elif self.path == "/mission":
            self.send_response(301)
            self.send_header("Location", "/mission/")
            self.end_headers()
        else:
            self.proxy_control_ui()

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        self.proxy_control_ui()

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), ProxyHandler)
    print(f"Proxy running on http://127.0.0.1:{PORT}")
    print(f"  /mission/ -> {MISSION_ROOT}/")
    print(f"  /*         -> {CONTROL_UI}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()
