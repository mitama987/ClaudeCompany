"""X (Twitter) credentials loader.

Lookup order:
  1. Environment variables: X_AUTH_TOKEN, X_CT0
  2. ~/.config/x-credentials/.env
  3. <repo-root>/.env  (gitignored)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values


@dataclass(frozen=True)
class XCredentials:
    auth_token: str
    ct0: str


def _candidate_env_files() -> list[Path]:
    home_cfg = Path.home() / ".config" / "x-credentials" / ".env"
    repo_root = Path(__file__).resolve().parents[2]
    return [home_cfg, repo_root / ".env"]


def load_credentials() -> XCredentials:
    auth_token = os.environ.get("X_AUTH_TOKEN")
    ct0 = os.environ.get("X_CT0")

    if not (auth_token and ct0):
        for path in _candidate_env_files():
            if not path.is_file():
                continue
            values = dotenv_values(path)
            auth_token = auth_token or values.get("X_AUTH_TOKEN")
            ct0 = ct0 or values.get("X_CT0")
            if auth_token and ct0:
                break

    if not auth_token or not ct0:
        raise RuntimeError(
            "X credentials not found. Set X_AUTH_TOKEN and X_CT0 via env vars "
            "or place them in ~/.config/x-credentials/.env or <repo>/.env"
        )

    return XCredentials(auth_token=auth_token, ct0=ct0)
