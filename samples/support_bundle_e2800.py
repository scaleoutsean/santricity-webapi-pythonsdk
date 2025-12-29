#!/bin/env python
"""
Sample: Generate and download a support bundle from a SANtricity controller.

This version uses environment-driven configuration (SANTRICITY_HOST, SANTRICITY_USER,
SANTRICITY_PASS, SANTRICITY_VERIFY_SSL, SANTRICITY_CA_BUNDLE) and accepts an
optional `--systemid` argument. It avoids proxy-specific logic used in older
examples.
"""
import argparse
import os
import pprint
import sys
from time import sleep

from netapp.santricity.api.v2.diagnostics_api import DiagnosticsApi
from netapp.santricity.api.v2.file_management_api import FileManagementApi
from netapp.santricity.api_client import ApiClient, Configuration
from netapp.santricity.models.v2.support_data_request import SupportDataRequest
from netapp.santricity.rest import ApiException


def main():
    parser = argparse.ArgumentParser(description="Request and download support bundle")
    parser.add_argument("--systemid", help="System ID (or SANTRICITY_ID env)")
    parser.add_argument("--password", help="Password (or SANTRICITY_PASS env)")
    parser.add_argument("--host", help="Controller host (or SANTRICITY_HOST env)")
    args = parser.parse_args()

    config = Configuration()
    # Environment-driven configuration (direct SANtricity by default)
    config.host = args.host or os.getenv("SANTRICITY_HOST", "https://controller_a:8443")
    config.username = os.getenv("SANTRICITY_USER", "admin")
    config.password = args.password or os.getenv("SANTRICITY_PASS", "rw")

    verify = os.getenv("SANTRICITY_VERIFY_SSL")
    if verify is None:
        config.verify_ssl = True
    else:
        config.verify_ssl = verify.lower() in ("1", "true", "yes")

    ca = os.getenv("SANTRICITY_CA_BUNDLE")
    if ca:
        config.ssl_ca_cert = ca

    api_client = ApiClient()
    config.api_client = api_client

    system_id = args.systemid or os.getenv("SANTRICITY_ID")
    if not system_id:
        print("Missing system id: provide --systemid or set SANTRICITY_ID")
        sys.exit(1)

    diagnostics_api = DiagnosticsApi()

    data_request = SupportDataRequest()
    data_request.type = "supportBundle"
    data_request.filename = "support_bundle"

    try:
        initial_response = diagnostics_api.start_support_data_retrieval_request(
            system_id, body=data_request
        )
    except ApiException:
        print("An error occurred retrieving the support bundle.")
        sys.exit(1)

    print("Response from DiagnosticsApi.start_support_data_retrieval:\n")
    pprint.pprint(initial_response)

    try:
        bundle_ready = False
        while not bundle_ready:
            request_status = diagnostics_api.get_support_data_retrieval_request_status(
                system_id, initial_response.request_id
            )
            print(
                "request complete percentage: {}".format(
                    request_status.progress.percentage
                )
            )
            bundle_ready = request_status.progress.complete
            sleep(5)
    except ApiException:
        print("An error occurred retrieving the support bundle.")
        sys.exit(1)

    file_api = FileManagementApi()
    try:
        file_list = file_api.get_scratch_file()
    except ApiException:
        print("Could not get the list of files")
        sys.exit(1)

    file_found = None
    for file_info in file_list:
        if file_info.file_name == data_request.filename:
            print(f"Found file, ready to download: {file_info.file_name}")
            file_found = file_info
            break

    if file_found:
        try:
            resp = file_api.get_file_from_scratch_dir(
                file_found.file_name, auto_delete=True
            )
            print("Downloaded to file: {}".format(resp))
        except ApiException:
            print("Error getting file")


if __name__ == "__main__":
    main()
