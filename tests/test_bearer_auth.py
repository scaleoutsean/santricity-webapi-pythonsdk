import unittest

from netapp.santricity.configuration import Configuration
from netapp.santricity.api_client import ApiClient


class BearerAuthTest(unittest.TestCase):
    def test_bearer_token_header_applied(self):
        cfg = Configuration()
        cfg.access_token = "abc123"
        api = ApiClient()
        headers = {}
        querys = {}
        api.update_params_for_auth(headers, querys, ["bearerToken"])
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], "Bearer abc123")

    def test_bearer_token_preferred_over_basic(self):
        cfg = Configuration()
        cfg.access_token = "tok123"
        api = ApiClient()
        headers = {}
        querys = {}
        # Simulate generated method that still requests basicAuth
        api.update_params_for_auth(headers, querys, ["basicAuth"])
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], "Bearer tok123")

    def test_token_refresh_callback_used(self):
        cfg = Configuration()
        cfg.access_token = None
        cfg.token_refresh_callback = lambda: "refreshed-token"
        api = ApiClient()
        headers = {}
        querys = {}
        api.update_params_for_auth(headers, querys, ["basicAuth"])
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], "Bearer refreshed-token")


if __name__ == "__main__":
    unittest.main()
