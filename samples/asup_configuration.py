"""
The Clear BSD License

Copyright (c) – 2016, NetApp, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of NetApp, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys

from netapp.santricity.api.v2.device_asup_api import DeviceASUPApi
from netapp.santricity.api_client import ApiClient, Configuration
from netapp.santricity.models.v2.device_asup_update_request import \
    DeviceAsupUpdateRequest
from netapp.santricity.rest import ApiException


def process_asup_settings(host, username, passwd):
    config = Configuration()
    # accept either a full URL (http(s)://...) or a bare host
    if host.startswith("http://") or host.startswith("https://"):
        config.host = host
    else:
        config.host = "https://" + host
    config.username = username
    config.password = passwd
    # Respect SANTRICITY_VERIFY_SSL environment variable
    verify = __import__("os").getenv("SANTRICITY_VERIFY_SSL")
    if verify is None:
        config.verify_ssl = True
    else:
        config.verify_ssl = verify.lower() in ("1", "true", "yes")

    # If verify_ssl is true then the certificate file should me made available.
    # This avoids insecure request warnings. Make the certificate available as illustrated below

    # config.ssl_ca_cert = "C:/prox-cert-export.pem"

    # Create a client object to use with the above defined configuration.
    api_client = ApiClient()
    config.api_client = api_client

    dev_asup = DeviceASUPApi(api_client)

    try:
        # Get the config info
        dev_asup_config = dev_asup.get_asup_configuration()
    except ApiException as ae:
        print("There was an exception: {}.".format(ae.reason))
        sys.exit()

    print(dev_asup_config)
    print("---------------------")

    # Now Update config info
    # Populate the required fileds as necessary and then call update_asup_configuration()
    # The below example is for illustration only. change/populate asup_updt_req fileds as necessary.

    asup_updt_req = DeviceAsupUpdateRequest()

    asup_updt_req.asup_enabled = True

    try:
        # Update config info
        asup_resp = dev_asup.update_asup_configuration(body=asup_updt_req)

    except ApiException as ae:
        print("There was an exception: {}.".format(ae.reason))
        sys.exit()


# Reads the array info from a config file and processes asup config info as necessary.
# It's assumed that the array and login details are as per this (asup_cfg.txt) sample file contents.


def main():
    # First, try to read local config file if present
    try:
        with open("asup_cfg.txt") as fp:
            lines = fp.readlines()
            for line in lines:
                if not line.startswith("#"):
                    fields = line.split()
                    process_asup_settings(fields[0], fields[1], fields[2])
    except FileNotFoundError:
        # Fall back to environment variables
        import os

        if os.getenv("SANTRICITY_HOST"):
            process_asup_settings(
                os.getenv("SANTRICITY_HOST"),
                os.getenv("SANTRICITY_USER", "rw"),
                os.getenv("SANTRICITY_PASS", "rw"),
            )


if __name__ == "__main__":
    main()
