"""HTTP client factory for X (Twitter) authenticated requests."""

from __future__ import annotations

import httpx

from .config import XCredentials, load_credentials

WEB_BEARER = (
    "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D"
    "1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def build_client(creds: XCredentials | None = None) -> httpx.Client:
    if creds is None:
        creds = load_credentials()

    cookies = {"auth_token": creds.auth_token, "ct0": creds.ct0}
    headers = {
        "authorization": f"Bearer {WEB_BEARER}",
        "x-csrf-token": creds.ct0,
        "user-agent": DEFAULT_USER_AGENT,
        "accept": "*/*",
        "accept-language": "ja,en-US;q=0.9,en;q=0.8",
        "x-twitter-active-user": "yes",
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-client-language": "ja",
    }
    return httpx.Client(
        base_url="https://x.com/i/api",
        cookies=cookies,
        headers=headers,
        timeout=30.0,
        follow_redirects=True,
    )
