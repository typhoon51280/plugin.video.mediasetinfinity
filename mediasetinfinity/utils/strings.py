from mediasetinfinity.utils import string_types
from codequick.support import CallbackRef
import json

def string_join(ids, separator=","):
    if isinstance(ids, string_types):
        return ids
    elif hasattr(ids, '__iter__'):
        return separator.join(ids)
    else:
        return ""

class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__json__'):
            if callable(o.__json__):
                return o.__json__()
            else:
                return o.__json__
        try:
            return super(CustomEncoder, self).default(o)
        except TypeError:
            return None

def tojson(obj):
    return json.dumps(obj, cls=CustomEncoder)
