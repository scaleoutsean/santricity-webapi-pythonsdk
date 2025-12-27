#NetApp SANtricity WebAPI - Python SDK

[![Build Status](https://github.com/scaleoutsean/santricity-webapi-pythonsdk/actions/workflows/mountebank-ci.yml/badge.svg)](https://github.com/scaleoutsean/santricity-webapi-pythonsdk/actions/workflows/mountebank-ci.yml)

##Requirements

The NetApp SANtricity WebAPI - Python SDK client library requires current Python 3.

**NOTE:** the SDK is unlikely to work until latest SANtricity API without adjustments and fixes. The idea is to fix what we need 

##Installation

###setuptools Installation

Installation of the Python bindings can be performed through [setuptools](http://pypi.python.org/pypi/setuptools).

Once downloaded, enter the following command:

```python
python setup.py install
```

###Manual Installation

If you chose not install the Python bindings through setuptools, you can perform the
installation manually by first downloading the latest release of the package. Once
downloaded, enter the following command to import the package:

```python
import netapp.santricity
```

###Getting started

To get started using the NetApp SANtricity WebAPI - Python SDK, access the ``api_client.py`` file and specify
the host URL for your REST service.

Here's a sample code for using NetApp SANtricity WebAPI - Python SDK:


```python
#/usr/bin/env python3

from netapp.santricity.configuration import Configuration
from netapp.santricity.api_client import ApiClient
from netapp.santricity.api.v2.storage_systems_api import StorageSystemsApi
from netapp.santricity.models.v2.storage_system_response import StorageSystemResponse
from pprint import pprint

config = Configuration()
config.host = "http://localhost:8443" #
config.username = "rw"
config.password = "rw"

api_client = ApiClient()
config.api_client = api_client

storage_system = StorageSystemsApi(api_client=api_client)

ssr = storage_system.get_all_storage_systems()
```

### Generating Documentation
API documentation can be generated in a format that suites you.

Available formats are:
* html
* pickle
* json
* applehelp  
* epub
* epub3
* latex
* text
* man
* texinfo
* gettext
* xml

For all options run:
```make
make -f docs/Makefile help
```
To generate html documentation:
```
cd docs
make -f Makefile html
```
#### Prerequisites
* Python3 interpreter
* urllib3
* Sphinx (sudo apt-get install python-sphinx -y)

