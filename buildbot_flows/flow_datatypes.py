import json

class generic_node_container(object):
    def __init__(self,*args,**kwargs):
        self.data = dict()
        self.data.update(self._object_defaults)

        # Identify the object types from the defaults
        self.obj_types = dict([(key,type(value)) for key,value
                            in self._object_defaults.items()])

        # Map any passed values to the container
        for key in kwargs:
            self[key] = kwargs[key]
        
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        # Don't allow new fields to be set
        if key not in self:
            msg = "{} not a key in {} node, will not create new fields."
            raise KeyError(msg.format(key,type(self)))
        
        # Check the type of the new value
        if not isinstance(value, self.obj_types[key]):
            msg = "{} is expected to be {}, passed {}"
            raise TypeError(msg.format(key,self.obj_types[key],type(value)))
        self.data[key] = value

    def __repr__(self):
        return str(self.data)

    def keys(self):
        return self.data.keys()

    def types(self):
        return self.obj_types

    def get_id(self):
        print self

    def __iter__(self):
        for x in self.data:
            yield x

    def json(self):
        return json.dumps(self.data, indent=2)



#######################################################################
'''
Each node in the graphdb is a contract that the following fields will
exist, be of the type listed, and will be populated with the default
value if none is given.
'''
#######################################################################

class flow(generic_node_container):
    _object_defaults = {
        "cost"    : 0.00,
        "version" : 1.0,
        "author"  : "",
        "owner"   : "",
        "description" : "",
        "fulfillment" : "",
    }


class validation(generic_node_container):
    _object_defaults = {
        "command"  : "",
        "success"  : "",
        "failure"  : "",
    }

