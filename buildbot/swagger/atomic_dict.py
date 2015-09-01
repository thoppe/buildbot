from atom.api import Atom, Unicode, Range, Bool, Int, Float, Typed
import json

class SAtom(Atom):
    _required = []
    
    def __init__(self,*args,**kwargs):
        super(Atom,self).__init__(*args,**kwargs)
        state = self.as_dict()
        for key in self._required:
            if not state[key]:
                msg = "Key '{}' in class {} is required"
                raise ValueError(msg.format(key,self.__class__.__name__))

    def as_dict(self):
        # Only pass along items that are not empty
        # numeric types are always passe through
        obj = self.__getstate__()
        for key,val in obj.items():
            if not val and val!=0:
                obj.pop(key)
        return obj
        
    def __repr__(self):
        return str(self.as_dict())


class License(SAtom):
    name = Unicode()
    url  = Unicode()
    _required = ["name"]

class Contact(SAtom):
    name = Unicode()
    url  = Unicode()
    emai = Unicode()

class Info(SAtom):
    title = Unicode()
    version = Unicode()
    description = Unicode()
    termsOfService = Unicode()
    license = Typed(License)
    contact = Typed(Contact)
    _required = ["title", "version"]

A = License(name="bob",url='http')
X = Info(title="test",version="1.0",license=A)
print X
exit()
    

class Person(Atom):
    """ A simple class representing a person object.

    """
    last_name  = Unicode()
    first_name = Unicode()

    age = Range(low=0)

    debug = Bool(False)



data = {"name":"sam", "age":2}
A = Person(first_name = 3)
print A
