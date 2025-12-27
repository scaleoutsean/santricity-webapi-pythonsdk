"""
Create a small checked-in example fixture `example_mappings.json` from `mappings.sanitized.json`.
This selects the first N mappings and truncates bodies larger than a threshold.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SANITIZED = os.path.join(DATA_DIR, "mappings.sanitized.json")
OUT = os.path.join(os.path.dirname(__file__), "example_mappings.json")

MAX_ITEMS = 20
MAX_BODY = 16 * 1024  # 16 KB


def make_example(src=SANITIZED, out=OUT, max_items=MAX_ITEMS, max_body=MAX_BODY):
    if not os.path.exists(src):
        raise SystemExit(f"Sanitized mappings not found: {src}")
    with open(src, "r", encoding="utf-8") as fh:
        mappings = json.load(fh)
    example = []
    for m in mappings[:max_items]:
        m2 = dict(m)
        b = m2.get("body")
        if b and isinstance(b, str) and len(b) > max_body:
            m2["body"] = b[:max_body] + "\n...TRUNCATED..."
        example.append(m2)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(example, fh, indent=2, ensure_ascii=False)
    print(f"Wrote example mappings to {out} ({len(example)} entries)")


if __name__ == "__main__":
    make_example()
