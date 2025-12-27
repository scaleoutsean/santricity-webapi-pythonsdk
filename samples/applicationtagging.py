"""
The Clear BSD License

Copyright (c) – 2016, NetApp, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of NetApp, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
#This is a sample code that illustrates SDK usage for creating & collecting volumes based on application tagging

from netapp.santricity.rest import ApiException
from netapp.santricity.api_client import ApiClient
from netapp.santricity.api_client import Configuration
from netapp.santricity.api.v2.workloads_api import WorkloadsApi
from netapp.santricity.models.v2.workload_create_request import WorkloadCreateRequest

import sys


config = Configuration()

#use URL of the proxy or embedded server/controller and appropriate credentials
#NOTE:Modify the below variable to match your configuration.

config.host = "http://localhost:8080"
config.username = "rw"
config.password = "rw"

#For a proxy it assumes that the array is already added and its ID is "c5". For embedded, the array ID is 1.
#NOTE:Modify the below variable to match the array ID.

sys_id="c5"


#Create a client object to use with the above defined configuration.
api_client = ApiClient()
config.api_client = api_client

wld_api=WorkloadsApi(api_client)

#Create a new workload and retrieve all defined work-loads

wrk_load_cr_req=WorkloadCreateRequest()

wrk_load_cr_req.name="NoSQL"

try:
    #Create a work load
    wrk_load_model= wld_api.new_workload(sys_id,data=wrk_load_cr_req)
    print("Created workload. Name: %s , ID : %s" %(wrk_load_model.name,wrk_load_model.id))

    #Get the list of all defiend work-loads
    wrk_load_model_list = wld_api.get_all_defined_workloads(sys_id)
    print("Defined Workloads :", wrk_load_model_list)

except ApiException as ae:
    print("There was an exception: {}.".format(ae.reason))
    sys.exit()








