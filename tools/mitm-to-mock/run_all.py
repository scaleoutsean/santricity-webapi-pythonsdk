"""
Run full pipeline: sanitize -> convert flows -> create mappings -> post imposter -> run tests.
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TOOLS = os.path.dirname(__file__)
DATA = os.path.join(TOOLS, "data")


def run(cmd, **kw):
    print("RUN:", cmd)
    res = subprocess.run(cmd, shell=True, cwd=ROOT, **kw)
    if res.returncode != 0:
        raise SystemExit(res.returncode)


def main():
    # 1) sanitize if mappings exists
    mappings = os.path.join(TOOLS, "data", "mappings.json")
    sanitized = os.path.join(TOOLS, "data", "mappings.sanitized.json")
    if os.path.exists(mappings):
        run(f"python3 {TOOLS}/sanitize_mappings.py")
    else:
        print("No raw mappings found; expecting", sanitized)

    if not os.path.exists(sanitized):
        print("No sanitized mappings found; aborting")
        sys.exit(2)

    # 2) build example fixture
    run(f"python3 {TOOLS}/create_example_fixture.py")

    # 3) post imposter
    run(f"python3 {TOOLS}/convert_to_mountebank.py --mappings {sanitized}")

    # 4) run tests pointing at mountebank
    env = os.environ.copy()
    env["SANTRICITY_HOST"] = "http://localhost:5000"
    # run nosetests via the run_tests_with_host script
    run(f"python3 {TOOLS}/run_tests_with_host.py", env=env)


if __name__ == "__main__":
    main()
