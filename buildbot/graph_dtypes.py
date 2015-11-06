import json
from copy import deepcopy
from traits.api import Int, Str, Float, Either, Dict, Any, Unicode
from traits.api import HasPrivateTraits

_python_traits_mapper = {
    str : Str,
    int : Int,
    unicode : Str,
    float : Float,
}


# Schema.org code disabled for now
# from schemas.schema_org_manager import schema_org
#def load_context(context):
#    if not context:
#        return {}
#    if context["@context"] == u'http://schema.org':
#        field_keys = schema_org[context["@type"]]
#    else:
#        msg = "Context {} unknown".format(context["@context"])
#        raise KeyError(msg)
#    # Assume field_keys are defaulted to strings
#    defaults = [u""]*len(field_keys)
#    return dict(zip(field_keys,defaults))

class neo4j_container(HasPrivateTraits):
    ''' This shouldn't be called to create a node/edge, but to create an instance of one. '''

    _object_types = {}
    
    def __init__(self,**kwargs):
        super(neo4j_container, self).__init__(**kwargs)        

    def __repr__(self):
        return str(self.dict())

    def keys(self):
        return [key for key in self.trait_names()
                if key[0] != "_" and "trait_" not in key]

    def json(self,indent=2):
        return json.dumps(self.dict(),indent=indent)

    def dict(self):
        js = {}
        for key in self.keys():
            js[key] = self[key]
        return js

    def __iter__(self):
        for x in self.keys():
            yield x
            
    def __getitem__(self, key):
        return self.get(key)[key]
    
    def __setitem__(self, key, value):
        self.trait_set(**{key:value})

    def set(self, **kwargs):
        self.trait_set(**kwargs)

    def __eq__(self, other):
        return self.dict() == other.dict()

    #def types(self):
    #    return self._obj_types

#####################################################################################


def node_container(**container_kwargs):

    assert("label" in container_kwargs)
    default_label = container_kwargs.pop('label')

    class node_factory(neo4j_container):

        id    = Either(None,Int)
        label = Str(default_label)

        def __init__(self, id=None, **kwargs):
            self.id = id            
            super(node_factory, self).__init__(**kwargs)

        def dict(self):
            data = super(node_factory, self).dict()
            data["label"] = self.label
            data["id"]    = self.id
            return data

    node = node_factory
    node.__name__ = str(default_label)
    
    for key,value in container_kwargs.items():
        obj_type = type(value)
        trait = _python_traits_mapper[obj_type](value)
        node.add_class_trait(key, trait)
        node._object_types[key] = obj_type

    return node

##############################################################################

def edge_container(**container_kwargs):

    assert("label" in container_kwargs)
    default_label = container_kwargs.pop('label')

    assert("start" in container_kwargs)
    default_start = container_kwargs.pop('start')

    assert("end" in container_kwargs)
    default_end = container_kwargs.pop('end')

    class edge_factory(neo4j_container):

        label = Str(default_label)
        start = Str(default_start)
        end   = Str(default_end)

        start_id = Either(None,Int)
        end_id   = Either(None,Int)
        id       = Either(None,Int)

        def __init__(self, n1, n2, id=None, **kwargs):
            self.id = id            
            super(edge_factory, self).__init__(**kwargs)


            if type(n1) is int and type(n2) is int:
                idx1 = n1
                idx2 = n2
            elif n1.id is None or n2.id is None:
                msg = "Nodes must have an ID before an edge can be created"
                raise ValueError(msg)
            else:
                idx1 = n1.id
                idx2 = n2.id

            self.start_id = idx1
            self.end_id   = idx2

        def __repr__(self):
            s = "{} -[{}]> {} ".format(self.start, self.label, self.end)
            return s + super(edge_factory, self).__repr__()

    edge = edge_factory
    edge.__name__ = "{}_{}_{}".format(default_start,default_label,default_end)
    
    for key,value in container_kwargs.items():
        trait = _python_traits_mapper[type(value)](value)
        edge.add_class_trait(key, trait)

    return edge
        
    
if __name__ == "__main__":
    pass

    #simple = node_container(dog="a",mom=3,x=20)
    #a = simple(dog="cat")
    #a.label= 'foo'
    #a.mom= 4

    #pair = node_container(x=3, y=4)
    #b = pair()
    #print a
    #print b

