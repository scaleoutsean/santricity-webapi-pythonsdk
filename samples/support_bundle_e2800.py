#!/bin/env python
"""
The Clear BSD License

Copyright (c) – 2016, NetApp, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of NetApp, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import argparse
import pprint
import sys
from time import sleep

import urllib3

from netapp.santricity.api.v2.diagnostics_api import DiagnosticsApi
from netapp.santricity.api.v2.file_management_api import FileManagementApi
from netapp.santricity.api.v2.storage_systems_api import StorageSystemsApi
from netapp.santricity.api_client import ApiClient
from netapp.santricity.configuration import Configuration
from netapp.santricity.models.v2.support_data_request import SupportDataRequest
from netapp.santricity.models.v2.support_data_response import \
    SupportDataResponse
from netapp.santricity.rest import ApiException

parser = argparse.ArgumentParser()
parser.add_argument(
    "-p",
    "--proxy",
    default="",
    help="The base URL for the proxy. Ex. http://proxyhost.mydomain.com:8080",
)
parser.add_argument(
    "-a", "--api", default="v2", help='Specify the API to use. Default="v2"'
)
parser.add_argument(
    "--password", default="rw", help="The password to use for HTTP basic auth."
)
parser.add_argument(
    "--systemid", default="", help="Specify the system-id of the storage array."
)

args = parser.parse_args()
if not args.proxy:
    print("Missing mandatory argument (--proxy)")
    sys.exit()
if not args.systemid:
    print("Missing mandatory argument (-systemid)")
    sys.exit()

# This will disable warnings for unverified HTTPS requests.
# This is not recommended, but added here to clean up output.
urllib3.disable_warnings()

# Create a configuration object and set the appropriate parameters
api_configuration = Configuration()
api_configuration.password = args.password
api_configuration.host = args.proxy
# For demonstration purposes, let's disable SSL verification
api_configuration.verify_ssl = False

# Now create the generic ApiClient object
# The ApiClient will utilize the Configuration object automatically
client = ApiClient()
# remove this prior to release
# print("client:\n{}".format(client.__dict__))
storage_api = StorageSystemsApi()
# remove this prior to release
# print("storage_api: \n{}".format(storage_api.__dict__))
diagnostics_api = DiagnosticsApi()
data_request = SupportDataRequest()  # type, filename
data_request.type = "supportBundle"
data_request.filename = "sampledata"
try:
    initial_response = diagnostics_api.start_support_data_retrieval_request(
        args.systemid, body=data_request
    )
except ApiException:
    print("An error occurred retrieving the support bundle.")
    sys.exit()
print("Response from DiagnosticsApi.start_support_data_retrieval:\n")
pprint.pprint(initial_response)
# Now we need to wait a bit for the bundle to be generated
# Lets check on the status periodically so we know when it's done
try:
    bundle_ready = False
    while not bundle_ready:
        request_status = diagnostics_api.get_support_data_retrieval_request_status(
            args.systemid, initial_response.request_id
        )
        print(
            "request complete percentage: {}".format(request_status.progress.percentage)
        )
        bundle_ready = request_status.progress.complete
        sleep(5)
except ApiException:
    print("An error occurred retrieving the support bundle.")
    sys.exit()
# Now the bundle should be ready to download
# We can just download it, but let's verify the file is there first
file_api = FileManagementApi()
try:
    file_list = file_api.get_scratch_file()
except ApiException:
    print("Could not get the list of files")
    sys.exit()
file_found = False
for file_info in file_list:
    if file_info.file_name == data_request.filename:
        print(
            "The file was found on the proxy. Ready to download: {}".format(
                file_info.file_name
            )
        )
        file_found = True
if file_found:
    try:
        resp = file_api.get_file_from_scratch_dir(file_info.file_name, auto_delete=True)
        print("Downloaded to file: {}".format(resp))
    except ApiException:
        print("Error getting file")
