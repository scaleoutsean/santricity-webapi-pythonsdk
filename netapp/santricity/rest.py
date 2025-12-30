"""
 The Clear BSD License

 Copyright (c) – 2016, NetApp, Inc. All rights reserved.

 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

 * Neither the name of NetApp, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


import io
import json
import logging
import ssl

import certifi

from .configuration import Configuration

# python 2 and python 3 compatibility library


try:
    import urllib3
except ImportError:
    raise ImportError("Swagger Python client requires urllib3.")

try:
    # for python3
    from urllib.parse import urlencode
except ImportError:
    # for python2
    from urllib.parse import urlencode


logger = logging.getLogger(__name__)


class RESTResponse(io.IOBase):
    def __init__(self, resp):
        self.urllib3_response = resp
        self.status = resp.status
        self.reason = resp.reason
        self.data = resp.data

    def getheaders(self):
        """
        Returns a dictionary of the response headers.
        """
        return self.urllib3_response.getheaders()

    def getheader(self, name, default=None):
        """
        Returns a given response header.
        """
        return self.urllib3_response.getheader(name, default)


class RESTClientObject:
    def __init__(self, pools_size=4):
        # urllib3.PoolManager will pass all kw parameters to connectionpool
        # https://github.com/shazow/urllib3/blob/f9409436f83aeb79fbaf090181cd81b784f1b8ce/urllib3/poolmanager.py#L75
        # https://github.com/shazow/urllib3/blob/f9409436f83aeb79fbaf090181cd81b784f1b8ce/urllib3/connectionpool.py#L680
        # ca_certs vs cert_file vs key_file
        # http://stackoverflow.com/a/23957365/2985775

        # cert_reqs
        if Configuration().verify_ssl:
            cert_reqs = ssl.CERT_REQUIRED
        else:
            cert_reqs = ssl.CERT_NONE

        # ca_certs
        if Configuration().ssl_ca_cert:
            ca_certs = Configuration().ssl_ca_cert
        else:
            # if not set certificate file, use Mozilla's root certificates.
            ca_certs = certifi.where()

        # cert_file
        cert_file = Configuration().cert_file

        # key file
        key_file = Configuration().key_file

        # SSL context - handle Python 3.13+ urllib3 behavior
        ssl_context = None
        if not Configuration().verify_ssl:
            # When SSL verification is disabled, create a custom context that
            # also disables VERIFY_X509_PARTIAL_CHAIN and VERIFY_X509_STRICT
            # which urllib3 enables by default in Python 3.13+
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            # Clear the strict verification flags that can cause issues
            # even when CERT_NONE is set
            if hasattr(ssl, "VERIFY_X509_PARTIAL_CHAIN"):
                ssl_context.verify_flags &= ~ssl.VERIFY_X509_PARTIAL_CHAIN
            if hasattr(ssl, "VERIFY_X509_STRICT"):
                ssl_context.verify_flags &= ~ssl.VERIFY_X509_STRICT

        # https pool manager
        self.pool_manager = urllib3.PoolManager(
            num_pools=pools_size,
            cert_reqs=cert_reqs,
            ca_certs=ca_certs,
            cert_file=cert_file,
            key_file=key_file,
            ssl_context=ssl_context,
        )

    def request(
        self, method, url, query_params=None, headers=None, body=None, post_params=None
    ):
        """
        :param method: http request method
        :param url: http request url
        :param query_params: query parameters in the url
        :param headers: http request headers
        :param body: request json body, for `application/json`
        :param post_params: request post parameters,
                            `application/x-www-form-urlencode`
                            and `multipart/form-data`
        """
        method = method.upper()
        assert method in ["GET", "HEAD", "DELETE", "POST", "PUT", "PATCH", "OPTIONS"]

        if post_params and body:
            raise ValueError(
                "body parameter cannot be used with post_params parameter."
            )

        post_params = post_params or {}
        headers = headers or {}

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        try:
            # For `POST`, `PUT`, `PATCH`, `OPTIONS`
            if method in ["POST", "PUT", "PATCH", "OPTIONS"]:
                if query_params:
                    url += "?" + urlencode(query_params)
                if headers["Content-Type"] == "application/json":
                    if not isinstance(body, str):
                        body = json.dumps(body)
                    r = self.pool_manager.request(
                        method, url, body=body, headers=headers
                    )
                if headers["Content-Type"] == "application/x-www-form-urlencoded":
                    r = self.pool_manager.request(
                        method,
                        url,
                        fields=post_params,
                        encode_multipart=False,
                        headers=headers,
                    )
                if headers["Content-Type"] == "multipart/form-data":
                    # must del headers['Content-Type'], or the correct Content-Type
                    # which generated by urllib3 will be overwritten.
                    del headers["Content-Type"]
                    r = self.pool_manager.request(
                        method,
                        url,
                        fields=post_params,
                        encode_multipart=True,
                        headers=headers,
                    )
            # For `GET`, `HEAD`, `DELETE`
            else:
                r = self.pool_manager.request(
                    method, url, fields=query_params, headers=headers
                )
        except urllib3.exceptions.SSLError as e:
            msg = "{}\n{}".format(type(e).__name__, str(e))
            raise ApiException(status=0, reason=msg)

        r = RESTResponse(r)

        # In the python 3, the response.data is bytes.
        # we need to decode it to string.
        r.data = r.data.decode("utf8")

        # log response body
        logger.debug("response body: %s" % r.data)

        if r.status not in list(range(200, 206)):
            raise ApiException(http_resp=r)

        return r

    def GET(self, url, headers=None, query_params=None):
        return self.request("GET", url, headers=headers, query_params=query_params)

    def HEAD(self, url, headers=None, query_params=None):
        return self.request("HEAD", url, headers=headers, query_params=query_params)

    def OPTIONS(
        self, url, headers=None, query_params=None, post_params=None, body=None
    ):
        return self.request(
            "OPTIONS",
            url,
            headers=headers,
            query_params=query_params,
            post_params=post_params,
            body=body,
        )

    def DELETE(self, url, headers=None, query_params=None):
        return self.request("DELETE", url, headers=headers, query_params=query_params)

    def POST(self, url, headers=None, query_params=None, post_params=None, body=None):
        return self.request(
            "POST",
            url,
            headers=headers,
            query_params=query_params,
            post_params=post_params,
            body=body,
        )

    def PUT(self, url, headers=None, query_params=None, post_params=None, body=None):
        return self.request(
            "PUT",
            url,
            headers=headers,
            query_params=query_params,
            post_params=post_params,
            body=body,
        )

    def PATCH(self, url, headers=None, query_params=None, post_params=None, body=None):
        return self.request(
            "PATCH",
            url,
            headers=headers,
            query_params=query_params,
            post_params=post_params,
            body=body,
        )


class ApiException(Exception):
    def __init__(self, status=None, reason=None, http_resp=None):
        if http_resp:
            self.status = http_resp.status
            self.reason = http_resp.reason
            self.body = http_resp.data
            self.headers = http_resp.getheaders()
        else:
            self.status = status
            self.reason = reason
            self.body = None
            self.headers = None

    def __str__(self):
        """
        Custom error messages for exception
        """
        error_message = "({})\n" "Reason: {}\n".format(self.status, self.reason)
        if self.headers:
            error_message += "HTTP response headers: {}\n".format(self.headers)

        if self.body:
            error_message += "HTTP response body: {}\n".format(self.body)

        return error_message
