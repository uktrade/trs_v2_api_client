from apiclient.exceptions import APIRequestError


class NotFoundError(APIRequestError):
    """A 404 was returned from the API."""

    pass
