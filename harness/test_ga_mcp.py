"""Standalone Google Analytics MCP server connection smoke test.

This script spawns the local `analytics-mcp` process, performs the MCP
stdio handshake, lists available tools, and optionally runs a tiny GA4
report. It proves the MCP path works before we wire it into the analytics
agent.

Usage:
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
    export GOOGLE_CLOUD_PROJECT=your-gcp-project-id
    export GA_PROPERTY_ID=123456789   # optional; used for run_report test
    ./harness/venv/bin/python harness/test_ga_mcp.py

If you do not have analytics-mcp installed:
    ./harness/venv/bin/pip install git+https://github.com/googleanalytics/google-analytics-mcp.git
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any


class StdioMCPClient:
    """Minimal MCP client over stdio for the Google Analytics MCP server."""

    PROTOCOL_VERSION = "2024-11-05"

    def __init__(self, command: list[str], env: dict[str, str] | None = None):
        self.command = command
        self.env = {**os.environ, **(env or {})}
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._next_id = 1
        self._pending: dict[int, Any] = {}
        self._reader_thread: threading.Thread | None = None
        self._initialized = False

    def __enter__(self) -> StdioMCPClient:
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()
        return None

    def start(self) -> None:
        self._proc = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.env,
            bufsize=1,
        )
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()
        self.initialize()

    def stop(self) -> None:
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.wait()
        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=2)

    def _read_loop(self) -> None:
        """Read JSON-RPC responses from the server stdout."""
        assert self._proc is not None and self._proc.stdout is not None
        for line in self._proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            req_id = msg.get("id")
            if req_id is not None and req_id in self._pending:
                event = self._pending.pop(req_id)
                event["response"] = msg
                event["event"].set()

    def _send(self, msg: dict) -> int:
        assert self._proc is not None and self._proc.stdin is not None
        with self._lock:
            req_id = self._next_id
            self._next_id += 1
        msg["jsonrpc"] = "2.0"
        msg["id"] = req_id
        payload = json.dumps(msg) + "\n"
        self._proc.stdin.write(payload)
        self._proc.stdin.flush()
        return req_id

    def _request(self, method: str, params: dict | None = None,
                 timeout: float = 60) -> dict:
        event = {"event": threading.Event(), "response": None}
        req_id = self._send({"method": method, "params": params or {}})
        self._pending[req_id] = event
        if not event["event"].wait(timeout=timeout):
            self._pending.pop(req_id, None)
            raise TimeoutError(f"Request {method} timed out")
        resp = event["response"]
        if resp is None:
            raise RuntimeError(f"No response for {method}")
        if "error" in resp:
            raise RuntimeError(f"{method} failed: {resp['error']}")
        return resp.get("result", {})

    def _notify(self, method: str, params: dict | None = None) -> None:
        msg = {"method": method, "params": params or {}}
        msg["jsonrpc"] = "2.0"
        payload = json.dumps(msg) + "\n"
        assert self._proc is not None and self._proc.stdin is not None
        self._proc.stdin.write(payload)
        self._proc.stdin.flush()

    def initialize(self) -> dict:
        res = self._request("initialize", {
            "protocolVersion": self.PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "aagman-ga-mcp-test", "version": "0.1.0"},
        })
        self._notify("notifications/initialized", {})
        self._initialized = True
        return res

    def list_tools(self) -> list[dict]:
        return self._request("tools/list").get("tools", [])

    def call_tool(self, name: str, arguments: dict | None = None) -> Any:
        res = self._request("tools/call", {
            "name": name,
            "arguments": arguments or {},
        })
        content = res.get("content", [])
        if not content:
            return None
        text = content[0].get("text", "")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text


def _fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip() or os.environ.get("GOOGLE_PROJECT_ID", "").strip()
    property_id = os.environ.get("GA_PROPERTY_ID", "").strip()

    if not credentials:
        _fail("GOOGLE_APPLICATION_CREDENTIALS not set.")
    if not Path(credentials).exists():
        _fail(f"Credentials file not found: {credentials}")
    if not project:
        _fail("GOOGLE_CLOUD_PROJECT not set.")

    repo = Path(__file__).resolve().parent.parent
    analytics_mcp_bin = repo / "harness" / "venv" / "bin" / "analytics-mcp"
    if not analytics_mcp_bin.exists():
        _fail(f"analytics-mcp not found at {analytics_mcp_bin}. Run: ./harness/venv/bin/pip install git+https://github.com/googleanalytics/google-analytics-mcp.git")

    env = {
        "GOOGLE_APPLICATION_CREDENTIALS": credentials,
        "GOOGLE_CLOUD_PROJECT": project,
    }

    print(f"Spawning MCP server: {analytics_mcp_bin}")
    print(f"Project: {project}")
    print(f"Credentials: {credentials}")

    with StdioMCPClient([str(analytics_mcp_bin)], env=env) as client:
        print("\n--- Available tools ---")
        tools = client.list_tools()
        for tool in tools:
            print(f"  - {tool.get('name')}: {tool.get('description', '')[:80]}")

        print("\n--- Account summaries ---")
        try:
            summaries = client.call_tool("get_account_summaries", {})
            print(json.dumps(summaries, indent=2, default=str)[:2000])
        except Exception as e:
            print(f"get_account_summaries failed: {e}")

        if property_id:
            print(f"\n--- Run report on property {property_id} ---")
            try:
                report = client.call_tool("run_report", {
                    "property_id": property_id,
                    "metrics": [{"name": "screenPageViews"}],
                    "date_ranges": [{"start_date": "7daysAgo", "end_date": "today"}],
                })
                print(json.dumps(report, indent=2, default=str)[:2000])
            except Exception as e:
                print(f"run_report failed: {e}")

    print("\nMCP connection test complete.")


if __name__ == "__main__":
    main()
