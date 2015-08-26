'''
The buildbot_contract manager loads and validates a swagger file.
'''
import json
from swagger_spec_validator.validator20 import validate_spec

class buildbot_contract(object):

    def __init__(self, f_swagger):
        self.load_contract(f_swagger)
        self.schemes = self.data["schemes"]
        self.base_path = self.data["basePath"]
        self.paths = self.data["paths"]

    def load_contract(self, f_swagger):
        with open(f_swagger) as FIN:
            raw = FIN.read()
            js  = json.loads(raw)
        
        if validate_spec(js) is None:
            self.data = js
            return True

        msg = "Bad swaggerfile {}".format(f_swagger)
        raise SyntaxError(msg)

    def keys(self):
        return self.paths.keys()

