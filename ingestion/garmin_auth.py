"""Garmin Connect login with token caching.

First run: logs in with GARMIN_EMAIL / GARMIN_PASSWORD (asks for an MFA code if
enabled) and saves tokens to .garmin_tokens/. Later runs reuse the tokens, so
no password or MFA is needed until they expire.
"""
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from garminconnect import Garmin

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

TOKEN_DIR = Path(os.getenv("GARMIN_TOKEN_DIR", ROOT / ".garmin_tokens"))


def get_client() -> Garmin:
    # 1) try cached tokens
    try:
        client = Garmin()
        client.login(str(TOKEN_DIR))
        return client
    except Exception:
        pass
    # 2) fall back to credentials (+ MFA prompt), which saves the tokens
    client = Garmin(
        os.environ["GARMIN_EMAIL"],
        os.environ["GARMIN_PASSWORD"],
        prompt_mfa=lambda: input("Garmin MFA code: ").strip(),
    )
    client.login(str(TOKEN_DIR))
    return client


if __name__ == "__main__":
    c = get_client()
    print("Logged in as:", c.get_full_name())
    summary = c.get_user_summary(date.today().isoformat())
    print("Steps today:", summary.get("totalSteps"))
