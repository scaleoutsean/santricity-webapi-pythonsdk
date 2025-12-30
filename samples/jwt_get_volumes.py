"""
Sample that demonstrates using a JWT/Bearer token to call VolumesApi.get_all_volumes

Environment variables used:
- SANTRICITY_HOST (default: https://localhost:8443)
- SANTRICITY_TOKEN (required for this sample)
- SANTRICITY_ID (default: 1)
"""
import os
import pprint
import sys

from netapp.santricity.api.v2.volumes_api import VolumesApi
from netapp.santricity.api_client import ApiClient, Configuration
from netapp.santricity.rest import ApiException


def main():
    token = os.getenv("SANTRICITY_TOKEN")
    if not token:
        print("SANTRICITY_TOKEN is required for this sample")
        sys.exit(1)

    config = Configuration()
    config.host = os.getenv("SANTRICITY_HOST", "https://localhost:8443")
    # Set the token (Configuration already reads SANTRICITY_TOKEN from env by default)
    config.access_token = token

    api_client = ApiClient()
    config.api_client = api_client

    sys_id = os.getenv("SANTRICITY_ID", "1")

    volumes_api = VolumesApi(api_client)

    try:
        vols = volumes_api.get_all_volumes(sys_id)
        pprint.pprint(vols)
    except ApiException as ae:
        print("API exception:", ae)


if __name__ == "__main__":
    main()
