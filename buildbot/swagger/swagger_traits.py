from traits.api import Delegate, HasTraits, Instance,Int, Str

class Atom(HasTraits):
    _required = []
    
    def __init__(self,*args,**kwargs):
        super(HasTraits,self).__init__(*args,**kwargs)
        state = self.as_dict()
        for key in self._required:
            if key not in kwargs:
                msg = "Key '{}' in class {} is required"
                raise ValueError(msg.format(key,self.__class__.__name__))

    def as_dict(self):
        # Only pass along items that are not empty
        # numeric types are always passe through
        #help(self)
        obj = self.__getstate__()
        obj.pop("__traits_version__")
        for key,val in obj.items():
            if not val and val!=0:
                obj.pop(key)
        return obj
        
    def __repr__(self):
        return str(self.as_dict())

class License(Atom):
    name = Str()
    url  = Str()
    _required = ["name"]

class Contact(Atom):
    name = Str()
    url  = Str()
    emai = Str()

class Info(Atom):
    title   = Str()
    version = Str()
    description    = Str()
    termsOfService = Str()
    license = Instance(License)
    contact = Instance(Contact)
    _required = ["title", "version"]

    
A = License(name="bob",url='http')
print A
X = Info(title="test",version="1.0",license=A)
print X
exit()
    

class Person(Atom):
    """ A simple class representing a person object.

    """
    last_name  = Str()
    first_name = Str()

    age = Range(low=0)

    debug = Bool(False)



data = {"name":"sam", "age":2}
A = Person(first_name = 3)
print A
