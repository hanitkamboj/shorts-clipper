from __future__ import annotations

import json
import logging
import os
import pickle
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def get_youtube_service(client_secret_file: Path | str = "client_secret.json") -> Any:
    """Authenticate and return the YouTube service object.

    Handles token refresh, saved token loading, and desktop InstalledAppFlow login.
    """
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    token_path = Path(".cache/shorts-clipper/token.pickle")

    if token_path.exists():
        try:
            with open(token_path, "rb") as token:
                creds = pickle.load(token)  # noqa: S301
        except Exception as exc:
            log.warning("Failed to load existing token.pickle: %s", exc)
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(token_path, "wb") as token:
                    pickle.dump(creds, token)
                log.info("YouTube OAuth credentials refreshed successfully.")
            except Exception as e:
                token_path.unlink(missing_ok=True)
                log.warning("Token refresh failed: %s", e)
                creds = None

        if not creds or not creds.valid:
            # Check for client_secret file or env variable to authenticate via InstalledAppFlow
            secret_path = Path(client_secret_file)
            env_secret = os.environ.get("YOUTUBE_CLIENT_SECRET_JSON")

            if secret_path.exists() or env_secret:
                try:
                    from google_auth_oauthlib.flow import InstalledAppFlow

                    if env_secret:
                        client_config = json.loads(env_secret)
                        flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), scopes=SCOPES)

                    # Only run local server if we have an interactive console
                    log.info("Initiating Google OAuth login flow...")
                    creds = flow.run_local_server(port=0, open_browser=True)

                    token_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(token_path, "wb") as token:
                        pickle.dump(creds, token)
                    log.info("OAuth credentials saved successfully to %s", token_path)
                except Exception as exc:
                    raise RuntimeError(
                        f"YouTube OAuth login failed: {exc}. "
                        "Please verify your client_secret.json or link your channel via the web dashboard."
                    ) from exc
            else:
                raise RuntimeError(
                    "YouTube channel is not connected. "
                    "Please place your client_secret.json in the project root or link your account from the dashboard."
                )

    return build("youtube", "v3", credentials=creds)
