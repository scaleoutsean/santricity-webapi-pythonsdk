"""
The Clear BSD License

Copyright (c) – 2016, NetApp, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of NetApp, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# Sample code illustrates SDK usage for getting historical statistics for I/O Latency, IOPS & throughput
# Note: Enabling stats collection require certain parameters to be enabled in the wsconfig.xml.
# Please refer to the user guide for the details.


import os
import sys

from netapp.santricity.api.v2.statistics_api import StatisticsApi
from netapp.santricity.api_client import ApiClient, Configuration
from netapp.santricity.rest import ApiException


def main():
    config = Configuration()
    # Environment-driven configuration: prefer direct SANtricity host by default.
    config.host = os.getenv("SANTRICITY_HOST", "https://localhost:8443")
    sys_id = os.getenv("SANTRICITY_ID", "1")

    config.username = os.getenv("SANTRICITY_USER", "rw")
    config.password = os.getenv("SANTRICITY_PASS", "rw")

    # Create a client object to use with the above defined configuration.
    api_client = ApiClient()
    config.api_client = api_client

    stat_api = StatisticsApi(api_client)

    # Get All raw stats.
    try:
        stat_response = stat_api.get_all_historical_raw_performance_statistics(sys_id)
    except ApiException as ae:
        print("There was an exception: {}.".format(ae.reason))
        sys.exit()

    print(stat_response)


if __name__ == "__main__":
    main()
