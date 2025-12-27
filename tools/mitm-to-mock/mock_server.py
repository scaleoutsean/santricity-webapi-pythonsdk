"""
A minimal Flask mock server that loads mappings.json (array of {method,path,status,headers,body})
and serves responses for exact method+path matches.
"""
import json
import os
from urllib.parse import urlparse

from flask import Flask, make_response, request

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MAPPINGS_FILE = os.path.join(DATA_DIR, "mappings.json")

app = Flask(__name__)
_mappings = []


def load_mappings():
    global _mappings
    if not os.path.exists(MAPPINGS_FILE):
        print("Mappings file not found; create it using convert_flows.py")
        _mappings = []
        return
    with open(MAPPINGS_FILE, "r", encoding="utf-8") as fh:
        _mappings = json.load(fh)


def match_mapping(method, path):
    # first try exact method+path
    for m in _mappings:
        if m.get("method") == method and m.get("path") == path:
            return m
    # try path-only (ignore query)
    parsed = urlparse(path)
    short_path = parsed.path
    for m in _mappings:
        m_parsed = urlparse(m.get("path", ""))
        if m.get("method") == method and m_parsed.path == short_path:
            return m
    return None


@app.before_first_request
def _load():
    load_mappings()


@app.route(
    "/",
    defaults={"u_path": ""},
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
)
@app.route(
    "/<path:u_path>",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
)
def all_routes(u_path):
    full_path = "/" + u_path
    if request.query_string:
        full_path = (
            full_path + "?" + request.query_string.decode("utf-8", errors="replace")
        )
    mapping = match_mapping(request.method, full_path)
    if not mapping:
        return make_response(("Not found", 404))
    resp = make_response((mapping.get("body", ""), mapping.get("status", 200)))
    for k, v in mapping.get("headers", {}).items():
        resp.headers[k] = v
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
