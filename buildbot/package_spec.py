from peacock.atom import simple_atom, atom

# TO DO: let a buildbot_package be constrained by traits
from traits.api import Int, Str, Float, List, Enum
from traits.api import Bool, Any, Dict, Either
from traits.api import Instance

PropertyType = Either(Int,Str,Float,Bool)

class PropertySet(simple_atom):
    data = Dict(Str, PropertyType)

class Meta(atom):
    title = Str
    author = Str
    description = Str
    version = Str
    _required = ["title","version"]

class Action(atom):
    pre  = Str
    post = Str
    input  = List(Str)
    output = List(Str)
    description = Str

class BuildbotPackage(atom):
    meta = Instance(Meta,())
    requires = List(Str)
    nodes    = Dict(Str, Instance(PropertySet))
    relationships = List(Either(Str, PropertySet))
    contracts     = List(Str)
    actions   = Dict(Str, Instance(Action))
    _required = ["meta","nodes","actions"]
   

if __name__ == "__main__":
    P = BuildbotPackage()
    ping = P.nodes["ping"] = PropertySet()
    ping['name'] = ""
    ping['IP_address'] = ""
    ping['timestamp'] = 0
    print P



