from json import JSONDecoder

from dateutil import parser
from dateutil.parser import ParserError
from dotwiz import DotWiz

class TRSObjectJSONDecoder(JSONDecoder):
    pass

def encode(string):
    value = None

    # maybe it is a datetime
    if isinstance(string, str) and len(string) in [24, 25, 26, 27] and "T" in string:
        try:
            value = parser.parse(string)
        except (ParserError, TypeError):
            pass
    return value or string
