from json import JSONDecodeError

from apiclient import exceptions
from apiclient.error_handlers import BaseErrorHandler
from apiclient.response import Response

from v2_api_client.exceptions import InvalidSerializerError, NotFoundError


class APIErrorHandler(BaseErrorHandler):
    @staticmethod
    def get_exception(response: Response) -> exceptions.APIRequestError:
        """Parses client errors to extract bad request reasons."""
        response = response.get_original()

        if response.status_code == 404:
            # This is a 404, deal with this accordingly
            return NotFoundError(message=f"The endpoint {response.url} could not be found")

        if response.status_code == 400:
            # 400 Bad request error, probably an invalid serializer, let's try and extract the
            # errors to make it easier to debug, if not, carry on as normal.
            try:
                response_json = response.json()
                if response_json.pop("exception_type", None) == "save_serializer_invalid_error":
                    # It's an invalid serializer exception, good!
                    return InvalidSerializerError(
                        serializer_class=response_json.pop("serializer_name", "unknown_serializer"),
                        field_errors=response_json
                    )
            except JSONDecodeError:
                # carry on treating as an unhandled error
                pass

        if 400 <= response.status_code < 500:
            # Client error
            error_class = exceptions.ClientError
        elif response.status_code >= 500:
            # Server error
            error_class = exceptions.ServerError
        else:
            # We don't know what's happened here
            error_class = exceptions.APIClientError

        try:
            # Let's try to get the JSON from the exception
            return error_class(response.json(), status_code=response.status_code)
        except JSONDecodeError:
            # There was an issue parsing the JSON, let's try and extract the error reason in
            # another way
            return error_class(response.reason, status_code=response.status_code)
