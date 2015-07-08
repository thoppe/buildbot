class node_container(object):
    def __init__(self,*args,**kwargs):
        
        self.data = dict()
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
            msg = "{} not a key in {} node, will not create new fields."
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

    def __eq__(self, other):
        return ((self.label==other.label) and
                (self.data ==other.data))

    def keys(self):
        return self.data.keys()

    def types(self):
        return self.obj_types

    def __iter__(self):
        for x in self.data:
            yield x
