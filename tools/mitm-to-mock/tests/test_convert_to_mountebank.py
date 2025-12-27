import os
import sys
import unittest

# ensure local tools folder is importable
TOOLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

import convert_to_mountebank as ctb


class TestConvertToMountebank(unittest.TestCase):
    def test_to_stub_includes_header_predicate(self):
        entry = {
            "method": "GET",
            "path": "/api/test?x=1",
            "headers": {
                "Authorization": "Bearer abc",
                "Content-Type": "application/json",
            },
            "status": 200,
            "body": '{"a":1}',
        }
        stub = ctb.to_stub(entry, strict_body=True, match_headers=["Authorization"])
        preds = stub.get("predicates", [])
        # expect method/path predicate + body predicate + header predicate
        self.assertTrue(
            any(
                "equals" in p
                and "headers" in p.get("equals", {})
                or ("headers" in p and isinstance(p.get("headers"), dict))
                for p in preds
            )
        )
        # strict body should include deepEquals
        self.assertTrue(any("deepEquals" in p for p in preds))

    def test_non_strict_body_omits_body_predicate_for_nonjson(self):
        entry = {
            "method": "POST",
            "path": "/api/upload",
            "headers": {"Content-Type": "text/plain"},
            "status": 201,
            "body": "plain text body",
        }
        stub = ctb.to_stub(entry, strict_body=False, match_headers=None)
        preds = stub.get("predicates", [])
        # body is plain text and non-strict mode should not add a body predicate
        self.assertFalse(
            any("equals" in p and "body" in p.get("equals", {}) for p in preds)
        )

    def test_build_imposter_sets_port(self):
        imp = ctb.build_imposter(
            [{"method": "GET", "path": "/p", "headers": {}, "status": 200, "body": ""}],
            port=4242,
        )
        self.assertEqual(imp.get("port"), 4242)


if __name__ == "__main__":
    unittest.main()
