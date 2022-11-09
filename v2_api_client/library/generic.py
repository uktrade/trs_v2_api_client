from v2_api_client.library import BaseAPIClient


class FeatureFlagsAPIClient(BaseAPIClient):
    base_endpoint = "django-feature-flags"


class FeedbackAPIClient(BaseAPIClient):
    base_endpoint = "feedback"
