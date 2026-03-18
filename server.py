#!/usr/bin/env python3
"""Simple HTTP server for redirect-checker with CSV auto-save and version history."""

import http.server
import json
import os
import glob
from datetime import datetime, timezone

PORT = 3000
DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(DIR, "review-state.csv")
HISTORY_DIR = os.path.join(DIR, "history")
MAX_HISTORY = 200
SNAPSHOT_INTERVAL = 10  # create snapshot every N status changes


def to_csv(rows):
    lines = ["line,from,to,status,notes"]
    for r in rows:
        notes = r.get("notes", "").replace('"', '""')
        lines.append(f'{r["line"]},"{r["from"]}","{r["to"]}","{r["status"]}","{notes}"')
    return "\n".join(lines) + "\n"


def prune_history():
    files = sorted(glob.glob(os.path.join(HISTORY_DIR, "review-state-*.csv")))
    while len(files) > MAX_HISTORY:
        os.remove(files.pop(0))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_POST(self):
        if self.path != "/save":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        redirects = body.get("redirects", [])
        change_count = body.get("changeCount", 0)

        csv = to_csv(redirects)

        # Always write canonical state
        with open(CSV_FILE, "w") as f:
            f.write(csv)

        # Snapshot on every SNAPSHOT_INTERVAL changes
        snapshot_created = False
        if change_count > 0 and change_count % SNAPSHOT_INTERVAL == 0:
            os.makedirs(HISTORY_DIR, exist_ok=True)
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            with open(os.path.join(HISTORY_DIR, f"review-state-{ts}.csv"), "w") as f:
                f.write(csv)
            prune_history()
            snapshot_created = True

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "snapshot": snapshot_created}).encode())

    def log_message(self, fmt, *args):
        # Quieter logging — skip GET for static assets
        if args and isinstance(args[0], str) and args[0].startswith("GET"):
            return
        super().log_message(fmt, *args)


if __name__ == "__main__":
    print(f"Redirect checker server on http://localhost:{PORT}")
    try:
        http.server.HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
