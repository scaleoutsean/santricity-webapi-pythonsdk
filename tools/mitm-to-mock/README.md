# mitm-to-mock

Purpose: capture real SDK traffic via `mitmproxy`, convert captures to a simple mapping, and run a lightweight Flask mock server for offline testing.

Layout:
- `docker-compose.yml` — runs `mitmproxy` and persists captures to `data/`.
- `data/` — directory where `flows.mitm`, `mappings.json`, and mitm CA cert will appear.
- `convert_flows.py` — read `flows.mitm` and produce `mappings.json`.
- `mock_server.py` — simple Flask server that serves responses from `mappings.json`.

Quick start (host):

1) Start mitmproxy in the tools folder:

```bash
cd tools/mitm-to-mock
docker compose up -d
```

2) Record flows while running tests (example):

```bash
# in tools/mitm-to-mock
# start a recorder in the background (writes ./data/flows.mitm)
docker run --rm -v "$PWD/data":/home/mitmproxy -w /home/mitmproxy mitmproxy/mitmproxy mitmdump -w /home/mitmproxy/flows.mitm &

# On your host, point SDK/tests at the proxy
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080
# If HTTPS, copy the mitmproxy CA from ./data and use REQUESTS_CA_BUNDLE as needed

# run tests on host (example)
.venv/bin/nosetests tests

# stop recorder
pkill -f mitmdump
```

3) Convert flows to mappings:

```bash
cd tools/mitm-to-mock
python3 -m pip install -r requirements.txt
python3 convert_flows.py
```

4) Run mock server:

```bash
python3 mock_server.py
# server listens on http://0.0.0.0:5000
```

5) Point SDK/tests at the mock server and run tests.

Notes:
- Sanitize `data/mappings.json` before committing; do not commit secrets or credentials.
- This scaffold aims to be a minimal starting point; use WireMock/mountebank for advanced matching/stateful scenarios.
 - This scaffold aims to be a minimal starting point; for richer matching/stateful scenarios we provide Mountebank support.

Mountebank (optional)
---------------------
1) Start compose (mitm + mountebank):

```bash
cd tools/mitm-to-mock
docker compose up -d mitm mountebank
```

2) Record flows using the `mitm` service as described above (flows go into `data/flows.mitm`).

3) Convert flows and post to Mountebank:

```bash
python3 -m pip install -r requirements.txt
python3 convert_flows.py
python3 convert_to_mountebank.py
```

By default this posts an imposter on port `5000`. Run `docker compose up -d test-runner` to run the test-runner inside the compose network (it will run the test command defined in the compose file).

Security: sanitize `data/mappings.json` before committing; do not commit secrets or credentials.

## Run example: full pipeline

```sh
cd tools/mitm-to-mock
python3 -m pip install -r requirements.txt
# make sure flows.mitm exists (run capture per README)
python3 run_all.py
```

Post with strict matching and header predicates:

```sh
python3 convert_to_mountebank.py --mappings data/mappings.sanitized.json --strict-body --match-headers Authorization,Content-Type
```

Header matching notes
---------------------
- Use `--match-headers` to include one or more headers in predicate matching (comma-separated). This is opt-in to avoid over-constraining stubs.
- Example: `--match-headers Authorization,Content-Type` will include equality predicates for the `Authorization` and `Content-Type` headers found in a recorded response.
- If you need to match request headers instead of response headers, ensure your recordings capture the request/response pair and extend the converter accordingly.
