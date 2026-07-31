"""Phase-1 TDD: telegram.py — stub-safe notifier (prints if unconfigured)."""
from harness_core.telegram import Telegram


def test_stub_when_no_token(capsys):
    t = Telegram()
    assert t.send("hi there") == "stub"
    assert "hi there" in capsys.readouterr().out


def test_stub_when_token_without_chat():
    assert Telegram(token="T").send("x") == "stub"


def test_sends_when_configured():
    calls = []
    t = Telegram(token="TOK", chat_id="CHAT",
                 poster=lambda url, data: calls.append((url, data)))
    assert t.send("hello") == "sent"
    url, data = calls[0]
    assert "botTOK" in url
    assert data["chat_id"] == "CHAT"
    assert data["text"] == "hello"


def test_notifier_returns_callable():
    t = Telegram()
    fn = t.notifier()
    assert fn("via callable") == "stub"
