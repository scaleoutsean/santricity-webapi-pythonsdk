import os
import unittest
from unittest import mock

import urllib3

import samples.jwt_token_refresh as sample
from netapp.santricity.configuration import Configuration


class FakeResp:
    def __init__(self, status=200, data=b'{"accessToken":"tok1","duration":100}'):
        self.status = status
        self.data = data


class TokenRefreshFlowTest(unittest.TestCase):
    @mock.patch.object(urllib3.PoolManager, "request", return_value=FakeResp())
    def test_token_refresh_callback_returns_token(self, mock_request):
        # Arrange: env for the sample's token_refresh_callback
        os.environ["SANTRICITY_HOST"] = "https://auth.example/devmgr/v2"
        # Ensure basic auth env vars exist for Configuration.get_basic_auth_token()
        os.environ["SANTRICITY_USER"] = "u"
        os.environ["SANTRICITY_PASS"] = "p"

        cfg = Configuration()
        cfg.access_token = None
        cfg.token_refresh_callback = sample.token_refresh_callback

        # Act
        hdr = cfg.get_access_token_header()

        # Assert
        self.assertEqual(hdr, "Bearer tok1")
        self.assertEqual(cfg.access_token, "tok1")
        mock_request.assert_called_once()
        called_args, called_kwargs = mock_request.call_args
        self.assertEqual(called_args[0], "POST")
        # Called URL should end with /access-token by default
        self.assertTrue(called_args[1].endswith("/access-token"))


if __name__ == "__main__":
    unittest.main()
