"""
Run nosetests after setting `Configuration().host` from `SANTRICITY_HOST` env var.
"""
import os
import sys

from netapp.santricity.configuration import Configuration

host = os.environ.get("SANTRICITY_HOST", "http://localhost:5000")
print("Setting SDK host to", host)
Configuration().host = host

# run nosetests programmatically
import nose

argv = ["nosetests", "-q"]
# allow passing additional args via env (rare)
extra = os.environ.get('NOSE_ARGS')
if extra:
    argv.extend(extra.split())

print("Running:", argv)
res = nose.run(argv=argv)
if not res:
    sys.exit(1)
