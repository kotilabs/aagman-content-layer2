#!/usr/bin/env python3
"""Send cold emails via Zapmail API with randomized variant assignment and throttling.

This is the script used for the 2026-08-08 batch (150 emails, 50 per variant).
It expects a JSON file at /tmp/today150_assignment.json with shape:

{
  "date": "2026-08-08T07:47:51.417780",
  "variants": {
    "1a": [{"rank": "1", "email": "...", "name": "..."}, ...],
    "2b": [...],
    "5b": [...]
  }
}

The assignment file was generated from the top 5,000 Google Sheet via gws CLI.
"""

import json
import random
import time
import requests
from datetime import datetime

# Zapmail credentials — loaded from environment in production.
API_KEY = "YOUR_API_KEY"
WORKSPACE_ID = "YOUR_WORKSPACE_ID"
SERVICE_PROVIDER = "GOOGLE"
API_URL = "https://api.zapmail.ai/api/v2/onebox/send-email"

HEADERS = {
    "x-auth-zapmail": API_KEY,
    "x-workspace-id": WORKSPACE_ID,
    "x-service-provider": SERVICE_PROVIDER,
    "Content-Type": "application/json",
}

TEMPLATES = {
    "1a": {
        "account": "sean@replyport.co",
        "subject": "Tired of opening ten tabs to research one stock?",
        "body": """Hey,

You start with one stock idea. Then it's Moneycontrol, Screener, Tickertape, AMFI, and three YouTube videos. By the end, you've forgotten what you were looking for.

I'm Aryan from Aagman (SEBI RIA: INA000021951), a small team of IIT engineers building your AI investing desk for Indian markets. Research, plan, and invest — without watching screens all day.

Aagman lets you ask for what you actually want — in English, Hinglish, Tamil, or Bengali:

"stocks with ROE above 15 and debt below 0.5"

"best ELSS funds with lowest expense ratio"

"which mutual funds hold Reliance?"

And once you find something worth acting on, you can set the plan right there. Same question. Same desk.

read about us here: https://dub.sh/aagman-invest-1a

Cheers,
Aryan

PS — When you invest, it routes through your existing broker. Zerodha, Motilal Oswal, more coming. Your money stays where it is.""",
    },
    "2b": {
        "account": "seth@replyport.co",
        "subject": "Research on Sunday. Invest on autopilot all week.",
        "body": """Hey,

You find a good stock on Sunday. Monday you're buried in work. By Friday, the price has moved and you did nothing.

I'm Aryan from Aagman (SEBI RIA: INA000021951), a small team of IIT engineers building your AI investing desk for Indian markets. Research, plan, and invest — without watching screens all day.

Aagman lets you set the plan and walk away:

"buy 100 shares of [stock name] if it closes below ₹2,900 this week. put a stop-loss 8% below my average buy price, and sell half if it goes up 25%."

It watches. It waits. It acts.

The same place you screen stocks is where you set the rule. The same place you set the rule is where it executes.

check us out: https://dub.sh/aagman-invest-2b

Cheers,
Aryan

PS — When you invest, it routes through your existing broker. Zerodha, Motilal Oswal, more coming. Your money stays where it is.""",
    },
    "5b": {
        "account": "dale@replyport.co",
        "subject": "One desk for your entire investing loop",
        "body": """Hey,

You research on one site. Check prices on another. Place orders on a third. Read news on a fourth.

I'm Aryan from Aagman (SEBI RIA: INA000021951), a small team of IIT engineers building your AI investing desk for Indian markets. Research, plan, and invest — without watching screens all day.

Aagman does it all in one conversation.

"best flexi cap funds"

"stocks with ROE above 15"

"buy Reliance if it drops to 2900"

Screen, plan, invest. No tab switching.

check us out: https://dub.sh/aagman-invest-5b

Cheers,
Aryan

PS — When it invests, it routes through your existing broker. Zerodha, Motilal Oswal, more coming. Your money stays where it is.""",
    },
}


def send_email(recipient, variant):
    template = TEMPLATES[variant]
    payload = {
        "account": template["account"],
        "to": recipient["email"],
        "subject": template["subject"],
        "body": template["body"],
    }

    for attempt in range(3):
        try:
            resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
            data = resp.json()
            if resp.status_code == 200 and data.get("success"):
                return {"success": True, "message_id": data.get("data", {}).get("messageId")}
            else:
                return {"success": False, "error": data.get("message", f"HTTP {resp.status_code}")}
        except Exception as e:
            if attempt == 2:
                return {"success": False, "error": str(e)}
            time.sleep(2 ** attempt)


def main():
    with open("/tmp/today150_assignment.json") as f:
        assignment_data = json.load(f)

    results = []
    total = 0
    success = 0
    failed = 0

    sends = []
    for variant in ["1a", "2b", "5b"]:
        for r in assignment_data["variants"][variant]:
            sends.append({"rank": r["rank"], "email": r["email"], "name": r["name"], "variant": variant})

    # Shuffle so we don't blast one variant or mailbox all at once.
    random.shuffle(sends)

    print(f"[{datetime.now().isoformat()}] Starting send of {len(sends)} emails with throttling...")
    print(f"Expected duration: ~{len(sends) * 45 // 60} minutes")

    for i, item in enumerate(sends, 1):
        total += 1
        result = send_email(item, item["variant"])
        result.update(item)
        results.append(result)

        if result["success"]:
            success += 1
            print(f"[{i}/{len(sends)}] OK {item['variant']} -> {item['email']}")
        else:
            failed += 1
            print(f"[{i}/{len(sends)}] FAIL {item['variant']} -> {item['email']} | ERROR: {result['error']}")

        # Persist progress after each send.
        with open("/tmp/send_today_150_results.json", "w") as f:
            json.dump({
                "started_at": assignment_data["date"],
                "completed_count": total,
                "success": success,
                "failed": failed,
                "results": results,
            }, f, indent=2)

        # Throttle: 30–60s random delay between sends.
        if i < len(sends):
            delay = random.uniform(30, 60)
            time.sleep(delay)

    print(f"\n[{datetime.now().isoformat()}] Done.")
    print(f"Total: {total} | Success: {success} | Failed: {failed}")


if __name__ == "__main__":
    main()
