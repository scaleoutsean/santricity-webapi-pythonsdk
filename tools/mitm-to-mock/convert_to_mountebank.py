"""
Convert simple mappings.json into a Mountebank imposter and POST it to the Mountebank admin API.
Expect mappings.json format: array of {method, path, status, headers, body}
"""
import argparse
import json
import os
import sys
from urllib.parse import urlparse

import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MAPPINGS_FILE = os.path.join(DATA_DIR, "mappings.json")
MB_ADMIN = os.environ.get("MOUNTEBANK_ADMIN", "http://localhost:2525")
IMPOSTER_PORT = int(os.environ.get("IMPOSTER_PORT", "5000"))


def load_mappings(path=MAPPINGS_FILE):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _build_method_path_predicate(entry):
    path = entry.get("path", "")
    parsed = urlparse(path)
    predicate_parts = []
    predicate_parts.append({"equals": {"method": entry.get("method")}})
    predicate_parts.append({"equals": {"path": parsed.path}})
    if parsed.query:
        # permissive contains on query string
        predicate_parts.append({"contains": {"path": parsed.query}})
    return {"and": predicate_parts}


def _body_predicate(entry, strict_body=False):
    body = entry.get("body")
    if not body:
        return None
    try:
        parsed = json.loads(body)
        if strict_body:
            return {"deepEquals": {"body": parsed}}
        else:
            # permissive: convert back to compact JSON string equality
            return {"equals": {"body": json.dumps(parsed, separators=(",", ":"))}}
    except Exception:
        if strict_body:
            return {"equals": {"body": body}}
        else:
            return None


def _header_predicates(entry, headers_to_match=None):
    headers = entry.get("headers") or {}
    preds = []
    if not headers_to_match:
        return preds
    for h in headers_to_match:
        v = headers.get(h)
        if v is None:
            continue
        preds.append({"equals": {"headers": {h: v}}})
    return preds


def to_stub(entry, strict_body=False, match_headers=None):
    predicates = []
    predicates.append(_build_method_path_predicate(entry))
    body_pred = _body_predicate(entry, strict_body=strict_body)
    if body_pred:
        predicates.append(body_pred)
    header_preds = _header_predicates(entry, match_headers)
    predicates.extend(header_preds)

    response = {
        "is": {
            "statusCode": int(entry.get("status", 200)),
            "headers": entry.get("headers", {}),
            "body": entry.get("body", ""),
        }
    }
    return {"predicates": predicates, "responses": [response]}


def build_imposter(mappings, port=IMPOSTER_PORT, strict_body=False, match_headers=None):
    stubs = [
        to_stub(m, strict_body=strict_body, match_headers=match_headers)
        for m in mappings
    ]
    imposter = {
        "port": port,
        "protocol": "http",
        "stubs": stubs,
    }
    return imposter


def post_imposter(imposter, admin=MB_ADMIN):
    url = admin.rstrip("/") + "/imposters"
    resp = requests.post(url, json=imposter)
    resp.raise_for_status()
    return resp.json()


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Convert mappings.json and post as Mountebank imposter"
    )
    p.add_argument("--mappings", default=MAPPINGS_FILE, help="mappings.json path")
    p.add_argument("--admin", default=MB_ADMIN, help="Mountebank admin URL")
    p.add_argument("--port", type=int, default=IMPOSTER_PORT, help="imposter port")
    p.add_argument(
        "--strict-body",
        action="store_true",
        help="Require deep body equality for JSON bodies",
    )
    p.add_argument(
        "--match-headers", help="Comma-separated header names to include in predicates"
    )
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    mappings = load_mappings(args.mappings)
    match_headers = None
    if args.match_headers:
        match_headers = [h.strip() for h in args.match_headers.split(",") if h.strip()]
    imp = build_imposter(
        mappings,
        port=args.port,
        strict_body=args.strict_body,
        match_headers=match_headers,
    )
    print(
        f"Posting imposter with {len(mappings)} stubs to {args.admin} on port {args.port}"
    )
    r = post_imposter(imp, admin=args.admin)
    print("Posted imposter:", r)


if __name__ == "__main__":
    if not os.path.exists(MAPPINGS_FILE):
        print("mappings.json not found in data/ — run convert_flows.py first")
        sys.exit(2)
    main()
