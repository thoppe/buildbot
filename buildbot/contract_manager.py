'''
The buildbot_contract manager loads and validates a swagger file.
'''
import os, json, requests, subprocess, tempfile
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


    
    
class buildbot_action(object):

    def __init__(self,name,data,pack):
        self.name = name
        self.data = data
        contracts = pack.contracts

        # Identify the [pre] contract
        self.pre_contract = None
        for contract in contracts.values():
            if contract.data["host"] in data["pre"]:
                self.pre_contract = contract

        assert(self.pre_contract is not None)
        
        # Assume for now that the [post] contract is internal
        # (this doesn't have to be true in the future)
        self.post_contract = data["post"]

        # Identify the code_entry point
        self.code_entry = os.path.abspath(pack.code_entry)


    def __call__(self,**kwargs):
        # Run the action and validate against the contract
        print "Running the action", self.name

        # Check that input data matches contract
        print "CONTRACT CHECK function input GOES HERE..."

        # Format url with "input" information?
        url = self.data["pre"]
        r = requests.get(url)

        # Assume data is JSON serlizable
        input_data = json.loads(r.content)

        # Check that input data from API matches contract
        print "CONTRACT CHECK API INPUT GOES HERE..."

        # Run the nodejs code
        print "Action {} input {}".format(self.name, input_data)

        output_data = self.nodejs_oneoff(input_data)
        print "CONTRACT CHECK OUTPUT GOES HERE..."

        print "Action {} output {}".format(self.name, output_data)

        


    def nodejs_oneoff(self, data):
        '''
        Uses nodejs to run a single function defined in code_entry.
        '''

        nodejs_template = '''
        var logic = require('{f_code_entry}');
        var data = {json_data};
        var result = logic.{function_name}(data);
        var output = JSON.stringify(result);
        console.log(output);
        '''
        args = {
            "f_code_entry":self.code_entry,
            "function_name":self.name,
            "json_data":json.dumps(data),
        }

        nodejs_code = nodejs_template.format(**args)
        cmd = "nodejs"

        with tempfile.NamedTemporaryFile() as temp:
            temp.write(nodejs_code)
            temp.flush()


            proc = subprocess.Popen([cmd,temp.name],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            output,err = proc.communicate()

            if err:
                msg = "Problem with nodejs code\n{}".format(err)
                raise SyntaxError(msg)


        output_data = json.loads(output)
        return output_data
    

