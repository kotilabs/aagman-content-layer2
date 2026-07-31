"""kill_switch.py — manual emergency stop.

A KILL file is the signal: present => stop. The loop checks is_killed() between
every unit of work and inside sleeps (via sleep_interruptible, chunked so a kill
is honoured within `chunk` seconds even during a long idle). PID file lets the
arm/disarm CLI find the running process.
"""
from __future__ import annotations

import time as _time
from pathlib import Path


class KillSwitch:
    def __init__(self, kill_path, pid_path=None):
        self.kill_path = Path(kill_path)
        self.pid_path = Path(pid_path) if pid_path else self.kill_path.parent / "PID"

    def is_killed(self) -> bool:
        return self.kill_path.exists()

    def arm(self):
        self.kill_path.parent.mkdir(parents=True, exist_ok=True)
        self.kill_path.write_text("kill")

    def disarm(self):
        if self.kill_path.exists():
            self.kill_path.unlink()

    def write_pid(self, pid: int):
        self.pid_path.parent.mkdir(parents=True, exist_ok=True)
        self.pid_path.write_text(str(pid))

    def read_pid(self):
        if not self.pid_path.exists():
            return None
        try:
            return int(self.pid_path.read_text().strip())
        except ValueError:
            return None

    def sleep_interruptible(self, total, chunk=10, sleeper=None) -> bool:
        """Sleep up to `total` seconds in `chunk`-second steps, checking the kill
        file between steps. Returns True if a kill was seen (interrupted)."""
        sleeper = sleeper or _time.sleep
        remaining = total
        while remaining > 0:
            if self.is_killed():
                return True
            step = min(chunk, remaining)
            sleeper(step)
            remaining -= step
        return self.is_killed()
