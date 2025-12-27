"""
The Clear BSD License

Copyright (c) – 2016, NetApp, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of NetApp, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

#This sample code demonstrates syslog configuration
#Please note this works for embedded mode only.

from netapp.santricity.rest import ApiException
from netapp.santricity.api_client import ApiClient
from netapp.santricity.api_client import Configuration
from netapp.santricity.api.v2.diagnostics_api import DiagnosticsApi
from netapp.santricity.models.v2.alert_syslog_server import AlertSyslogServer
from netapp.santricity.models.v2.alert_syslog_configuration import AlertSyslogConfiguration

import sys

from pprint import pprint

config = Configuration()

#use URL of the embedded server/controller and appropriate credentials
#NOTE:Modify the below variable to match your configuration.

config.host = "https://10.113.76.206:8443"
config.username = "rw"
config.password = "I2finiti!"
config.verify_ssl=False

#For embedded, the array ID is 1.

sys_id="1"

#Create a client object to use with the above defined configuration.
api_client = ApiClient()
config.api_client = api_client

diag_api=DiagnosticsApi(api_client)


#Poupulate values for setting syslog configuration

alert_sys_log_server = AlertSyslogServer()

#Set the syslog server address and port number.
#Below values are for example only

alert_sys_log_server.port_number="514"
alert_sys_log_server.server_name="10.113.76.204"

alert_serv_list = []

alert_serv_list.append(alert_sys_log_server)

alert_sys_log_config = AlertSyslogConfiguration()

alert_sys_log_config.syslog_receivers=alert_serv_list

alert_sys_log_config.default_facility=3
alert_sys_log_config.default_tag="StorageArray"


try:
    alert_config = diag_api.set_syslog_configuration(sys_id,body=alert_sys_log_config)

except ApiException as ae:
    print("There was an exception: {}.".format(ae.reason))
    sys.exit()


#Retreive syslog configuration and verify

try:
    alert_config = diag_api.get_syslog_configuration(sys_id)

except ApiException as ae:
    print("There was an exception: {}.".format(ae.reason))
    sys.exit()

print(alert_config)


#Send a test syslog message

try:
    alert_config = diag_api.test_syslog_send(sys_id)

except ApiException as ae:
    print("There was an exception: {}.".format(ae.reason))
    sys.exit()

