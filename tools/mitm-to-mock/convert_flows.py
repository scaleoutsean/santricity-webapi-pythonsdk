"""
Simple converter: read mitmproxy flow file and emit a mappings.json file.
Mappings are naive: exact method + path matching. Use as a starting point.
"""
import json
import os

from mitmproxy import http, io

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FLOWS_FILE = os.path.join(DATA_DIR, "flows.mitm")
MAPPINGS_FILE = os.path.join(DATA_DIR, "mappings.json")


def body_text(resp):
    try:
        return resp.get_text(strict=False)
    except Exception:
        try:
            return resp.content.decode("utf-8", errors="replace")
        except Exception:
            return ""


def convert(flows_file=FLOWS_FILE, out_file=MAPPINGS_FILE):
    mappings = []
    if not os.path.exists(flows_file):
        raise SystemExit(f"Flows file not found: {flows_file}")

    with open(flows_file, "rb") as fh:
        reader = io.FlowReader(fh)
        for flow in reader.stream():
            if not isinstance(flow, http.HTTPFlow):
                continue
            req = flow.request
            resp = flow.response
            if resp is None:
                continue
            entry = {
                "method": req.method,
                "path": req.path,
                "url": req.pretty_url,
                "status": getattr(resp, "status_code", getattr(resp, "status", None)),
                "headers": dict(resp.headers),
                "body": body_text(resp),
            }
            mappings.append(entry)

    with open(out_file, "w", encoding="utf-8") as fh:
        json.dump(mappings, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {len(mappings)} mappings to {out_file}")


if __name__ == "__main__":
    convert()
