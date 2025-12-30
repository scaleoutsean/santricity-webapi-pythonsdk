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

**Dealing with TLS issues**

Install TLS certificates that pass `urllib3`'s `VERIFY_X509_PARTIAL_CHAIN` and `VERIFY_X509_STRICT` checks.

If you can't or won't, try disabling validation, or download and use a CA bundle. Some environment variables you can use:

```sh
export SANTRICITY_VERIFY_SSL=false
export SANTRICITY_CA_BUNDLE=/path/to/ca-bundle.pem
```

Then:

```python
import requests

# Download CA cert from controller and use it in your config
config.ssl_ca_cert = 'controller-ca.pem'
config.verify_ssl = True  # Now enable verification with the proper CA
```

Or, for the updated samples that use environment-driven configuration (recommended):

```bash
# set controller and creds
export SANTRICITY_HOST=https://controller_a:8443
export SANTRICITY_USER=admin
export SANTRICITY_PASS=YOURPASS
# optional: disable verification in lab
export SANTRICITY_VERIFY_SSL=false
# run the support-bundle sample (or other samples)
python samples/support_bundle_e2800.py --systemid 1
```

JWT / Bearer token usage

If your controller supports JWT/Bearer tokens, set `SANTRICITY_TOKEN` and run the `jwt_get_volumes.py` sample which demonstrates token-based auth against the Volumes API:

```bash
export SANTRICITY_HOST=https://controller_a:8443
export SANTRICITY_TOKEN="<your-jwt-or-bearer-token>"
export SANTRICITY_ID=1
python samples/jwt_get_volumes.py
```

Token refresh sample

If you need the SDK to obtain tokens on-demand (for example using the
client_credentials grant), use the `jwt_token_refresh.py` sample which
demonstrates setting `Configuration.token_refresh_callback`.

Environment variables used by the sample:

- `SANTRICITY_TOKEN_URL`: token endpoint (e.g. `https://auth.example.com/oauth2/token`)
- `SANTRICITY_CLIENT_ID`: OAuth client id
- `SANTRICITY_CLIENT_SECRET`: OAuth client secret
- `SANTRICITY_HOST`: SANtricity controller base URL
- `SANTRICITY_VERIFY_SSL`: optional `false` to disable TLS verification in lab

Example (bash):

```bash
export SANTRICITY_HOST=https://controller_a:8443
export SANTRICITY_TOKEN_URL=https://auth.example.com/oauth2/token
export SANTRICITY_CLIENT_ID=myclient
export SANTRICITY_CLIENT_SECRET=mysecret
export SANTRICITY_VERIFY_SSL=false
python samples/jwt_token_refresh.py
```

The sample's `token_refresh_callback` will POST a `grant_type=client_credentials`
request to `SANTRICITY_TOKEN_URL`, parse the `access_token` and return it to the
SDK which will then use it as a Bearer token for API calls.

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
