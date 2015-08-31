from collections import namedtuple
from swagger_spec_validator.validator20 import validate_spec
from recordtype import recordtype



def fancy_record(name, keys, **kwargs):
    val_types = [kwargs[k] if k in kwargs else ""
                 for k in keys]
    defaults  = zip(keys,val_types)

    return recordtype(name, defaults)

info_keys = ['version',
             'title',
             'description',
             'contact']
obj = fancy_record('info', info_keys, contacts={})

x = obj(version=1.0)
print x
x.version *= 2
print x
exit()  


spec = namedtuple('sw',['swagger','info'])
info = namedtuple("info", ['version',
                           'title',
                           'description'
                           'contact'])

X = spec(swagger={},info={})
print X
exit()


class swagger_spec(object):
    def __init__(self):
        pass

    
