# NetApp SANtricity WebAPI - Python SDK

[![Build Status](https://github.com/scaleoutsean/santricity-webapi-pythonsdk/actions/workflows/mountebank-ci.yml/badge.svg)](https://github.com/scaleoutsean/santricity-webapi-pythonsdk/actions/workflows/mountebank-ci.yml)

## What is this thing?

It's an unofficial, revived fork of the old Python 2-based SDK.

This SDK is unlikely to (fully) work with current SANtricity API without adjustments and fixes. The idea is to fix what we need, when we need it.

Originaly (Python 2) this SDK used to default to using [WSP](https://hub.docker.com/r/netapp/eseries-webservices/) which was a [bad idea, so I routinely remove it when I see it](https://github.com/scaleoutsean/eseries-perf-analyzer) and is [even worse now](https://hub.docker.com/r/netapp/eseries-webservices/) - WSP was last updated "some 3 years ago" (according to Docker Hub) and must have a bunch of unaddressed CVEs making it completely unfit for production use.

This SDK isn't fully "suitable for production use" either but if we test what works and use that in production, there no reason to not deploy it in production.

This repository aims to make at least the basic volume-related operations usable (create, edit, delete).

Bugs are expected and can be fixed. Submit pull requests (with tests) or bug reports to contribute.

## Requirements

The NetApp SANtricity WebAPI - Python SDK client library requires current Python 3 and SANtricity >=11.90.

## Installation

### setuptools Installation

Installation of the Python bindings can be performed through [setuptools](http://pypi.python.org/pypi/setuptools).

Once downloaded, enter the following command:

```python
pytho3 setup.py install
```

### Manual Installation

If you chose not install the Python bindings through setuptools, you can perform the installation manually by first downloading the latest release of the package. Once downloaded, enter the following command to import the package:

```python
import netapp.santricity
```

### Getting started

To get started using the NetApp SANtricity WebAPI - Python SDK, access the `api_client.py` file and specify
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
config.host = "https://controller_b:8443" # do not use WSP - see NOTE above
config.username = "admin"
config.password = "YOURPASS"

api_client = ApiClient()
config.api_client = api_client

storage_system = StorageSystemsApi(api_client=api_client)

ssr = storage_system.get_all_storage_systems()
```

**Configuration via environment variables**

Samples and the test-runner now prefer direct SANtricity access by default. Use these environment variables to control behavior:

- `SANTRICITY_HOST`: full URL to the SANtricity controller (e.g. `https://10.0.0.5:8443`)
- `SANTRICITY_USER`: username (default `admin`)
- `SANTRICITY_PASS`: password (default `YOURPASS`)
- `SANTRICITY_ID`: system id for embedded mode (default `1`); we recommend to use `1` at most for initial authentication and the correct system_id (WWN) after that

Optional proxy mode with WSP (not recommended):

- `WSP_MODE=true` to enable WSP/proxy flow (opt-in only)
- `WSP_HOST`: host for the WSP proxy (e.g. `http://wsp.example:8080`)
- `WSP_TARGET`: target array id in the proxy (e.g. `c5`)

Examples:

Direct controller (recommended):
```bash
export SANTRICITY_HOST=https://10.0.0.5:8443
export SANTRICITY_USER=admin
export SANTRICITY_PASS=YOURPASS
python samples/view_historic_stats.py
```

Proxy/WSP (opt-in):
```bash
export WSP_MODE=true
export WSP_HOST=http://wsp.example:8080
export WSP_TARGET=c5
python samples/view_historic_stats.py
```

Security note: WSP centralizes access to multiple arrays behind a single service. If WSP is unmaintained or vulnerable it greatly increases risk - do not enable WSP in production; prefer direct controller access and only use WSP in isolated test environments where you understand the security implications.


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
```sh
make -f docs/Makefile help
```

To generate html documentation:
```sh
cd docs
make -f Makefile html
```

#### Prerequisites

* Python3 interpreter
* urllib3
* Sphinx (sudo apt install python3-sphinx -y)
