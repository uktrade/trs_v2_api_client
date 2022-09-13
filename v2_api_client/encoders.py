from django.core.serializers.json import DjangoJSONEncoder

from v2_api_client.library import TRSObject
import json

class TRSObjectJsonEncoder(DjangoJSONEncoder):
    """Custom encoder class used to encode TRSObjects."""

    def default(self, o):
        if isinstance(o, TRSObject):
            return json.dumps(o.data_dict.__dict__)
        return super().default(o)
