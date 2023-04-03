from apiclient.exceptions import APIRequestError, ClientError


class NotFoundError(APIRequestError):
    """A 404 was returned from the API."""

    status_code = 404


class InvalidSerializerError(ClientError):
    """400 returned from the API due to an invalid serializer"""

    status_code = 500

    def __init__(
        self, serializer_class, field_errors, message="", status_code=None, info=""
    ):
        super().__init__(message, status_code, info)
        self.serializer_class = serializer_class
        self.field_errors = field_errors

    def __str__(self):
        error_text = f"There were errors with the {self.serializer_class} serializer:"
        for field, value in self.field_errors.items():
            if isinstance(value, list):
                # It's a ValidationError from the API
                for error in value:
                    error_text += f"{field} ---- {error}\n"

        return error_text
