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
import urllib3

from netapp.santricity.configuration import Configuration
from netapp.santricity.api_client import ApiClient
from netapp.santricity.api.v2.volumes_api import VolumesApi


def token_refresh_callback():
    # Prefer explicit token URL, otherwise use controller host + standard path
    token_url = os.environ.get(
        "SANTRICITY_TOKEN_URL",
        os.environ.get("SANTRICITY_HOST", "http://localhost:8080/devmgr/v2").rstrip("/")
        + "/access-token",
    )

    # Duration for the issued token (controller-specific unit). Default to 100.
    duration = int(os.environ.get("SANTRICITY_TOKEN_DURATION", "100"))

    cfg = Configuration()
    basic = cfg.get_basic_auth_token()

    http = urllib3.PoolManager()
    body = json.dumps({"duration": duration})

    resp = http.request(
        "POST",
        token_url,
        headers={"Content-Type": "application/json", "Authorization": basic},
        body=body,
    )

    if resp.status != 200:
        raise RuntimeError(f"Token endpoint returned {resp.status}: {resp.data.decode()}")

    data = json.loads(resp.data.decode("utf-8"))
    # Controller returns `accessToken` (camelCase)
    token = data.get("accessToken")
    if not token:
        raise RuntimeError("No accessToken in token response")
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
