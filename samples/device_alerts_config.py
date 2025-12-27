"""
The Clear BSD License

Copyright (c) – 2016, NetApp, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of NetApp, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from netapp.santricity.rest import ApiException
from netapp.santricity.api_client import ApiClient
from netapp.santricity.api_client import Configuration
from netapp.santricity.api.v2.diagnostics_api import DiagnosticsApi
from netapp.santricity.models.v2.device_alert_configuration import DeviceAlertConfiguration

import sys


def process_alerts_settings(host,username,passwd):
    config = Configuration()
    config.host = "https://" + host
    config.username = username
    config.password = passwd
    config.verify_ssl=False

    #If verify_ssl is true then the certificate file should me made available.
    #This avoids insecure request warnings. Make the certificate available as illustrated below

    #config.ssl_ca_cert = "C:/prox-cert-export.pem"


    #Create a client object to use with the above defined configuration.
    api_client = ApiClient()
    config.api_client = api_client


    diag_api=DiagnosticsApi(api_client)

    try:
        #Get the config info
        dev_alert_cfg = diag_api.get_alert_configuration("1") # system_id=1 for embedded
    except ApiException as ae:
        print("There was an exception: {}.".format(ae.reason))
        sys.exit()

    print(dev_alert_cfg)
    print("---------------------")

    #Now Update config info
    #Populate the required fileds as necessary and then call update_asup_configuration()
    #The below example is for illustration only. change/populate updt_req fileds as necessary.

    updt_req= DeviceAlertConfiguration()

    updt_req.alerting_enabled=False
    updt_req.email_sender_address=""
    updt_req.email_server_address=""
    updt_req.send_additional_contact_information=False
    updt_req.additional_contact_information=""
    updt_req.recipient_email_addresses=[]

    try:
        #Update config info
        config_resp = diag_api.update_alert_configuration("1",updt_req)

    except ApiException as ae:
        print("There was an exception: {}.".format(ae.reason))
        sys.exit()

#Reads the array info from a config file and processes alerts config info as necessary.
#It's assumed that the array and login details are as per this (alerts_cfg.txt) sample file contents.

fp= open("alerts_cfg.txt")

lines=fp.readlines()
for line in lines:
    if not line.startswith("#"):
        fields=line.split()
        process_alerts_settings(fields[0],fields[1],fields[2])


