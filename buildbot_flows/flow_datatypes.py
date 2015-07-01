
class generic_node_container(object):
    def __init__(self,*args,**kwargs):
        self.data = dict()
        self.data.update(self._object_defaults)
        self.data.update(**kwargs)
        
    def __getitem__(self, key):
        return self.data[key]
    def __setitem__(self, key, value):
        self.data[key] = value
    def __repr__(self):
        return str(self.data)

    def keys(self):
        return self.data.keys()

    def get_id(self):
        print self

    def __iter__(self):
        for x in self.data:
            yield x

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
