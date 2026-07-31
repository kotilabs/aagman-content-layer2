"""telegram.py — stub-safe notifier.

If TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID are configured, send() posts to the Bot
API; otherwise it prints (so the harness runs fine with no Telegram set up). The
`poster` seam keeps it offline-testable.
"""
from __future__ import annotations

from typing import Callable


class Telegram:
    def __init__(self, token=None, chat_id=None, poster: Callable | None = None):
        self.token = token
        self.chat_id = chat_id
        self.poster = poster

    def send(self, text: str) -> str:
        if not (self.token and self.chat_id):
            print(f"[telegram stub] {text}")
            return "stub"
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        (self.poster or _http_post)(url, {"chat_id": self.chat_id, "text": text})
        return "sent"

    def notifier(self) -> Callable[[str], str]:
        return self.send


def _http_post(url, data):
    import requests
    requests.post(url, json=data, timeout=10)
