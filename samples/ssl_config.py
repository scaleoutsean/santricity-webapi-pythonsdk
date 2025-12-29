"""
The Clear BSD License

Copyright (c) – 2016, NetApp, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of NetApp, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# This sample code demonstrates how to use/configure signed certificates.

import os
import sys
from pprint import pprint

from netapp.santricity.api.v2.administration_api import AdministrationApi
from netapp.santricity.api_client import ApiClient, Configuration
from netapp.santricity.rest import ApiException


def main():
    config = Configuration()
    # Environment-driven configuration (direct SANtricity by default)
    config.host = os.getenv("SANTRICITY_HOST", "https://localhost:8443")

    config.username = os.getenv("SANTRICITY_USER", "admin")
    config.password = os.getenv("SANTRICITY_PASS", "admin")

    # TLS options
    verify = os.getenv("SANTRICITY_VERIFY_SSL")
    if verify is None:
        config.verify_ssl = True
    else:
        config.verify_ssl = verify.lower() in ("1", "true", "yes")
    ca = os.getenv("SANTRICITY_CA_BUNDLE")
    if ca:
        config.ssl_ca_cert = ca

    # Create a client object to use with the above defined configuration.
    api_client = ApiClient()
    config.api_client = api_client

    admin_api = AdministrationApi(api_client)

    try:
        ssl_config = admin_api.get_ssl_configuration()
    except ApiException as ae:
        print("There was an exception: {}.".format(ae.reason))
        sys.exit()

    print(ssl_config)
    print("--------------------------------------------")
    print("--------------------------------------------")

    # Upload a signed certificate (example path; replace with valid path)
    try:
        file_info = admin_api.upload_ca_certificate(file="/tmp/ca.cert.pem")
    except ApiException as ae:
        print("There was an exception: {}.".format(ae.reason))
        sys.exit()

    # Get the list of trusted certificates.
    try:
        cert_list = admin_api.get_trusted_certificate_authorities()
    except ApiException as ae:
        print("There was an exception: {}.".format(ae.reason))
        sys.exit()

    print("cert_list:")
    pprint(cert_list)
    print("--------------------------------------------")
    print("--------------------------------------------")

    # Remove a signed certificate (example alias; replace with real alias)
    ca_alias = "ae680996-897b-4c94-8d62-98d988b86215"
    try:
        admin_api.remove_ca(alias=ca_alias)
    except ApiException as ae:
        print("There was an exception: {}.".format(ae.reason))
        sys.exit()


if __name__ == "__main__":
    main()
