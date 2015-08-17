import json

class neo4j_container(object):
    _object_defaults = {}
    _context = {}
    
    def __init__(self,*args,**kwargs):        
        self.data = dict()

        # Download any context if needed
        if self._context:
            print "Load the schema information here!", self._context
            exit()

        
        self.data.update(self._object_defaults)

        # Identify the object types from the defaults,
        # use basestring to handle both str and unicode inputs
        self.obj_types = {}
        for key,value in self._object_defaults.items():
            if isinstance(value, str):
                vtype = basestring
            else:
                vtype = type(value)
            self.obj_types[key] = vtype

        # Map any passed values to the container
        for key in kwargs:
            self[key] = kwargs[key]
        
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        # Don't allow new fields to be set
        if key not in self:
            msg = "{} not a field in {}, will not create new fields."
            raise KeyError(msg.format(key,type(self)))
        
        # Check the type of the new value
        if not self.validate_type(key, value):
            msg = "{} is expected to be {}, passed {}"
            raise TypeError(msg.format(key,self.obj_types[key],type(value)))
        
        self.data[key] = value

    def validate_type(self, key, value):
        return isinstance(value, self.obj_types[key])

    def __repr__(self):
        return str(self.data)

    def keys(self):
        return self.data.keys()

    def types(self):
        return self.obj_types

    def __iter__(self):
        for x in self.data:
            yield x

class node_container(neo4j_container):
    
    label = None
    id    = None
    
    def __init__(self, id=None, *args, **kwargs):
        self.id = id
        super(node_container, self).__init__(*args, **kwargs)
        
    def __eq__(self, other):
        return ((self.label==other.label) and
                (self.data ==other.data))

    def json(self, indent=2):
        data = self.data.copy()
        data["id"]    = self.id
        data["label"] = self.label
        return json.dumps(data,indent=indent)

class edge_container(neo4j_container):
    
    label = None
    start = None
    end   = None

    start_id = None
    end_id   = None
    id       = None

    def __init__(self, n1, n2, id=None, *args, **kwargs):
        super(edge_container, self).__init__(*args, **kwargs)

        self.id = id

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
        return s + super(edge_container, self).__repr__()
    
    def __eq__(self, other):
        return ((self.label==other.label) and
                (self.start==other.start) and
                (self.end  ==other.end)   and
                (self.data ==other.data))

    def json(self,indent=2):
        data = self.data.copy()
        data["id"]    = self.id
        data["start_id"] = self.end_id
        data["end_id"]= self.start_id
        data["label"] = self.label
        data["start"] = self.start
        data["end"]   = self.end
        return json.dumps(data,indent=indent)


