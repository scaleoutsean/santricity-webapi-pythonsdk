"""
Sanitize `data/mappings.json` by redacting sensitive headers and JSON fields.
This produces `data/mappings.sanitized.json`.
"""
import json
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MAPPINGS_FILE = os.path.join(DATA_DIR, "mappings.json")
OUT_FILE = os.path.join(DATA_DIR, "mappings.sanitized.json")

SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie"}
SENSITIVE_KEYS = re.compile(r"(pass(word)?|token|auth|secret|credential|key|passwd)", re.I)


def redact_value(v):
    return "<REDACTED>"


+def walk_and_redact(obj):
+    if isinstance(obj, dict):
+        out = {}
+        for k, v in obj.items():
+            if SENSITIVE_KEYS.search(k):
+                out[k] = redact_value(v)
+            else:
+                out[k] = walk_and_redact(v)
+        return out
+    elif isinstance(obj, list):
+        return [walk_and_redact(x) for x in obj]
+    else:
+        return obj
+
+
+def sanitize_entry(entry):
+    # headers
+    headers = entry.get("headers") or {}
+    new_headers = {}
+    for hk, hv in headers.items():
+        if hk.lower() in SENSITIVE_HEADERS:
+            new_headers[hk] = redact_value(hv)
+        else:
+            new_headers[hk] = hv
+    entry["headers"] = new_headers
+
+    # body: if JSON, redact sensitive keys
+    b = entry.get("body")
+    if not b:
+        return entry
+    try:
+        parsed = json.loads(b)
+        sanitized = walk_and_redact(parsed)
+        entry["body"] = json.dumps(sanitized)
+    except Exception:
+        # not JSON, leave as-is
+        pass
+    return entry
+
+
+def sanitize(path=MAPPINGS_FILE, out=OUT_FILE):
+    if not os.path.exists(path):
+        raise SystemExit(f"Mappings file not found: {path}")
+    with open(path, "r", encoding="utf-8") as fh:
+        mappings = json.load(fh)
+    sanitized = [sanitize_entry(dict(m)) for m in mappings]
+    with open(out, "w", encoding="utf-8") as fh:
+        json.dump(sanitized, fh, indent=2, ensure_ascii=False)
+    print(f"Wrote sanitized mappings to {out}")
+
+
+if __name__ == "__main__":
+    sanitize()
