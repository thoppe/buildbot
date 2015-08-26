import sys, json
from swagger_spec_validator.validator20 import validate_spec

f_swagger = sys.argv[1]
with open(f_swagger) as FIN:
    raw = FIN.read()
    js  = json.loads(raw)

if validate_spec(js) is None:
    print "{} passed".format(f_swagger)
