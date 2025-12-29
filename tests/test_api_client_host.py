import unittest

from netapp.santricity.api_client import ApiClient
from netapp.santricity.configuration import Configuration


class ApiClientHostTest(unittest.TestCase):
    def test_missing_configuration_host_raises(self):
        cfg = Configuration()
        old = cfg.host
        try:
            cfg.host = None
            with self.assertRaises(ValueError):
                ApiClient()
        finally:
            cfg.host = old


if __name__ == "__main__":
    unittest.main()
