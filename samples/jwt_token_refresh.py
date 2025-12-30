#!/usr/bin/env python3
"""
Sample: token refresh callback using client_credentials grant.

Environment variables used:
- SANTRICITY_HOST
- SANTRICITY_VERIFY_SSL
- SANTRICITY_TOKEN_URL
- SANTRICITY_CLIENT_ID
- SANTRICITY_CLIENT_SECRET

This sample shows how to set `Configuration.token_refresh_callback` so the
SDK obtains an access token on demand.
"""
import os
import json
from urllib.parse import urlencode
import urllib3

from netapp.santricity.configuration import Configuration
from netapp.santricity.api_client import ApiClient
from netapp.santricity.api.v2.volumes_api import VolumesApi


def token_refresh_callback():
    token_url = os.environ.get("SANTRICITY_TOKEN_URL")
    client_id = os.environ.get("SANTRICITY_CLIENT_ID")
    client_secret = os.environ.get("SANTRICITY_CLIENT_SECRET")
    if not token_url or not client_id or not client_secret:
        raise RuntimeError(
            "Missing SANTRICITY_TOKEN_URL, SANTRICITY_CLIENT_ID or SANTRICITY_CLIENT_SECRET"
        )

    http = urllib3.PoolManager()
    body = urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    })

    resp = http.request(
        "POST",
        token_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=body,
    )

    if resp.status != 200:
        raise RuntimeError(f"Token endpoint returned {resp.status}: {resp.data.decode()}")

    data = json.loads(resp.data.decode("utf-8"))
    token = data.get("access_token")
    if not token:
        raise RuntimeError("No access_token in token response")
    return token


def main():
    cfg = Configuration()
    cfg.host = os.environ.get("SANTRICITY_HOST", "http://localhost:8080/devmgr/v2")
    cfg.verify_ssl = os.environ.get("SANTRICITY_VERIFY_SSL", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    cfg.token_refresh_callback = token_refresh_callback

    client = ApiClient(configuration=cfg)
    api = VolumesApi(api_client=client)

    try:
        vols = api.get_all_volumes()
        print("Found", len(vols), "volumes")
    except Exception as e:
        print("API call failed:", e)


if __name__ == "__main__":
    main()
