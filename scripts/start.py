#!/usr/bin/env python3
"""Start Job Finder: build the frontend if needed, run the server, open the browser
and trigger a scan, all in one command."""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_INDEX = ROOT / "web" / "dist" / "index.html"
ENV_FILE = ROOT / ".env"
URL = "http://127.0.0.1:8787"


def build_frontend(force: bool) -> None:
    if DIST_INDEX.exists() and not force:
        return
    print("Building frontend…")
    subprocess.run(["npm", "run", "build"], cwd=ROOT / "web", check=True)


def start_server() -> subprocess.Popen[bytes]:
    command = [str(ROOT / ".venv" / "bin" / "uvicorn"), "app.main:app", "--port", "8787"]
    if ENV_FILE.exists():
        command += ["--env-file", str(ENV_FILE)]
    return subprocess.Popen(command, cwd=ROOT)


def wait_for_health(timeout_seconds: int = 60) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"{URL}/api/health", timeout=2):
                return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.5)
    raise SystemExit("Server did not become healthy in time")


def trigger_scan() -> None:
    request = urllib.request.Request(f"{URL}/api/runs", data=b"", method="POST")
    try:
        with urllib.request.urlopen(request, timeout=5):
            print("Scan started.")
    except urllib.error.HTTPError as error:
        if error.code == 409:
            print("A scan is already running.")
        else:
            print(f"Could not start the scan: HTTP {error.code}")


def main() -> None:
    build_frontend(force="--rebuild" in sys.argv)
    server = start_server()
    try:
        wait_for_health()
        webbrowser.open(URL)
        trigger_scan()
        print(f"Job Finder running at {URL} — press Ctrl+C to stop.")
        server.wait()
    except KeyboardInterrupt:
        pass
    finally:
        server.terminate()
        server.wait()


if __name__ == "__main__":
    main()
