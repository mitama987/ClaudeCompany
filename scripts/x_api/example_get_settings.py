"""Smoke test: probe several endpoints to verify cookies + bearer work.

Usage:
    uv run python -m scripts.x_api.example_get_settings
"""

from __future__ import annotations

from .client import build_client

CANDIDATES = [
    ("GET", "/1.1/account/verify_credentials.json", None),
    ("GET", "/1.1/account/settings.json", None),
    ("GET", "/2/notifications/all.json", None),
    ("GET", "/1.1/dm/user_inbox.json", None),
    ("GET", "/1.1/users/lookup.json", {"user_id": "_self_"}),
    ("GET", "/1.1/help/settings.json", None),
]


def main() -> None:
    with build_client() as client:
        print(f"base_url: {client.base_url}")
        print(f"bearer:   ...{str(client.headers.get('authorization'))[-20:]}")
        print()
        for method, path, params in CANDIDATES:
            try:
                r = client.request(method, path, params=params)
                snippet = r.text[:120].replace("\n", " ")
                print(f"[{r.status_code}] {method} {path}")
                if r.status_code != 200:
                    print(f"      {snippet}")
                else:
                    try:
                        data = r.json()
                        keys = list(data.keys())[:8] if isinstance(data, dict) else type(data).__name__
                        print(f"      OK keys={keys}")
                    except Exception:
                        print(f"      OK ({len(r.text)} bytes)")
            except Exception as e:
                print(f"[ERR] {method} {path}: {e}")


if __name__ == "__main__":
    main()
