#!/usr/bin/env python3
"""Send Telegram notification.

Usage: python scripts/notify.py "message text"
   or: echo "message" | python scripts/notify.py

Reads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from environment or .env file.
"""
import json
import os
import sys
import urllib.request
import urllib.parse


def load_env():
    """Load .env file if it exists."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def send_telegram(message: str):
    """Send message via Telegram Bot API."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set", file=sys.stderr)
        sys.exit(1)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }).encode()

    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            if not result.get("ok"):
                print(f"Telegram API error: {result}", file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    load_env()

    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        message = sys.stdin.read().strip()
    else:
        print("Usage: notify.py 'message' or echo 'message' | notify.py", file=sys.stderr)
        sys.exit(1)

    send_telegram(message)
    print("Sent.")


if __name__ == "__main__":
    main()
