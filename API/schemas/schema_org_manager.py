import json, os

class schema_manager(dict):
    ''' Only loads the schema json once if called on. '''
    f_schema = "schema_org_all.json"

    def __getitem__(self, key):
        if not self:
            self.load_schema()
        return super(schema_manager,self).__getitem__(key)

    def load_schema(self):

        f = os.path.join(os.path.dirname(__file__),
                         self.f_schema)

        with open(f) as FIN:
            raw = FIN.read()
            js = json.loads(raw)
        
        for name in js["types"]:
            props = []
            props += js["types"][name]["specific_properties"]
            props += js["types"][name]["properties"]
            self[name] = props

schema_org = schema_manager()
