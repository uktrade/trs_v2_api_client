from apiclient import exceptions
from apiclient.error_handlers import BaseErrorHandler
from apiclient.response import Response


class APIErrorHandler(BaseErrorHandler):

    @staticmethod
    def get_exception(response: Response) -> exceptions.APIRequestError:
        """Parses client errors to extract bad request reasons."""
        if 400 <= response.get_status_code() < 500:
            json = response.get_json()
            return exceptions.ClientError(json)

        return exceptions.APIRequestError("something went wrong")
