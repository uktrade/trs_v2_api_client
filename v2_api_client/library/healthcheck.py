import requests
from django.conf import settings


def get_status():
    url = f"{settings.API_BASE_URL}/healthcheck"
    response = requests.get(url)
    return response.text
