"""First-run setup: detect browser, ensure CDP, verify LinkedIn login."""
import json
import shutil
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.json"

CDP_PORT = 9222

MAC_BROWSERS = [
    ("Arc", "/Applications/Arc.app/Contents/MacOS/Arc"),
    ("Google Chrome", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    ("Microsoft Edge", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ("Brave Browser", "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
]
LINUX_BROWSERS = ["arc", "google-chrome", "microsoft-edge", "brave-browser", "chromium"]
WIN_BROWSERS = [
    ("Arc", r"C:\Users\{user}\AppData\Local\Microsoft\WindowsApps\Arc.exe"),
    ("Google Chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    ("Google Chrome", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ("Microsoft Edge", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ("Brave Browser", r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"),
]


def detect_browser():
    """Return (name, executable_path) for the first installed Chromium browser, or None."""
    import os
    import sys
    if sys.platform == "darwin":
        for name, path in MAC_BROWSERS:
            if os.path.exists(path):
                return name, path
    elif sys.platform.startswith("linux"):
        for cmd in LINUX_BROWSERS:
            path = shutil.which(cmd)
            if path:
                return cmd, path
    elif sys.platform == "win32":
        import getpass
        for name, path in WIN_BROWSERS:
            path = path.replace("{user}", getpass.getuser())
            if os.path.exists(path):
                return name, path
    return None


def is_cdp_up(port: int = CDP_PORT) -> bool:
    try:
        with urllib.request.urlopen(f"http://localhost:{port}/json/version", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def ensure_cdp(browser, port: int = CDP_PORT) -> bool:
    """True if CDP is reachable; launches the browser with the debug port if needed."""
    if is_cdp_up(port):
        return True  # user's browser already exposes the port — don't relaunch
    name, path = browser
    subprocess.Popen(
        [path, f"--remote-debugging-port={port}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    deadline = time.time() + 15
    while time.time() < deadline:
        if is_cdp_up(port):
            return True
        time.sleep(0.5)
    return False


def _cdp(port: int, method: str, path: str):
    req = urllib.request.Request(f"http://localhost:{port}{path}", method=method)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def linkedin_logged_in(port: int = CDP_PORT) -> bool:
    """Open a tab on the LinkedIn feed via raw CDP HTTP and see where it lands.

    (Playwright connect_over_cdp hangs against Chrome 136+ browsers on the
    default profile — both the Python and Node clients — so this uses the
    plain /json/* CDP endpoints instead. Verified working with Chrome 151.)
    """
    tab = _cdp(port, "PUT", "/json/new?https://www.linkedin.com/feed/")
    tab_id = tab["id"]
    try:
        time.sleep(8)  # let redirects (authwall etc.) settle
        tabs = _cdp(port, "GET", "/json/list")
        mine = next((t for t in tabs if t.get("id") == tab_id), None)
        if not mine:
            return False
        url = mine.get("url", "").lower()
        title = mine.get("title", "").lower()
        bad = ("authwall", "login", "checkpoint", "signup", "uas/authenticate")
        return not any(b in url or b in title for b in bad)
    finally:
        try:
            _cdp(port, "GET", f"/json/close/{tab_id}")
        except Exception:
            pass


def run_setup() -> None:
    print("== Ajit engine setup ==\n")
    browser = detect_browser()
    if not browser:
        raise SystemExit(
            "No Chromium browser found (looked for Arc, Chrome, Edge, Brave, Chromium). "
            "Install one and re-run `python3 run.py setup`."
        )
    name, path = browser
    print(f"Browser: {name} ({path})")

    if is_cdp_up():
        print(f"CDP: already up on port {CDP_PORT} (using the running browser)")
    else:
        print(f"CDP: launching {name} with --remote-debugging-port={CDP_PORT} ...")
        if not ensure_cdp(browser):
            raise SystemExit(f"Browser launched but port {CDP_PORT} never came up. "
                             "Close all browser windows and try again.")
    print("CDP: OK")

    print("Checking LinkedIn login ...")
    while not linkedin_logged_in():
        input("\nA browser window is open on LinkedIn but you're not logged in.\n"
              "Log in there, then come back and press Enter to re-check ...")
        print("Re-checking LinkedIn login ...")
    print("LinkedIn: logged in")

    CONFIG.write_text(json.dumps({
        "browser_name": name,
        "browser_path": path,
        "cdp_port": CDP_PORT,
        "linkedin_verified_at": datetime.now(timezone.utc).isoformat(),
    }, indent=2) + "\n", encoding="utf-8")
    print(f"\nSetup complete — wrote {CONFIG}")


def check_ready():
    """True when ready, else a string describing what's missing. Non-interactive."""
    if not CONFIG.exists():
        return "no config.json — run `python3 run.py setup`"
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        port = int(config.get("cdp_port", CDP_PORT))
    except (ValueError, json.JSONDecodeError):
        return "config.json is unreadable — re-run `python3 run.py setup`"
    if not is_cdp_up(port):
        return (f"CDP port {port} is not up — start {config.get('browser_name', 'your browser')} "
                f"with --remote-debugging-port={port} (or re-run `python3 run.py setup`)")
    if not linkedin_logged_in(port):
        return "LinkedIn is not logged in on the CDP browser — log in, then re-check `status`"
    return True
