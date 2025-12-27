"""
The Clear BSD License

Copyright (c) – 2016, NetApp, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of NetApp, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

#This sample code demonstrates how to check if the needs attention is set for an array and then getting the details of it.

from netapp.santricity.api_client import ApiClient
from netapp.santricity.api_client import Configuration
from netapp.santricity.api.symbol.g_api import GApi
from netapp.santricity.api.v2.hardware_api import HardwareApi
from pprint import pprint
import os

config = Configuration()
# Environment-driven configuration (direct SANtricity by default)
WSP = os.getenv("WSP_MODE", "false").lower() in ("1", "true", "yes")
if WSP:
    config.host = os.getenv("WSP_HOST", "http://localhost:8080")
    sys_id = os.getenv("WSP_TARGET", "c5")
else:
    config.host = os.getenv("SANTRICITY_HOST", "http://localhost:8080")
    sys_id = os.getenv("SANTRICITY_ID", "1")

config.username = os.getenv("SANTRICITY_USER", "rw")
config.password = os.getenv("SANTRICITY_PASS", "rw")


#Create a client object to use with the above defined configuration.
api_client = ApiClient()
config.api_client = api_client


sym_api = GApi(api_client)

sa_data=sym_api.symbol_get_sa_data(sys_id)

# If Needs Attention is set then get the details.

if sa_data.needs_attention:
    print("Needs attention set for array:",sys_id)
    fail_list=sym_api.symbol_get_recovery_failure_list(sys_id)
    f_dict=fail_list.to_dict()

    #Now process the returned data to get the need attention items.
    for k,v in fail_list.to_dict().items():
        v_list=v
        for i in v_list:
            for k1, v1 in i.items():
                if (k1 == "rec_failure_type"):
                    continue
                if (v1):
                    print(k1,"--->",v1)
else:
    print("Array ",sys_id," is optimal")

