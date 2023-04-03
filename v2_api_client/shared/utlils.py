from typing import Union

import phonenumbers
from django.conf import settings

from v2_api_client.client import TRSAPIClient


def get_loa_document_bundle() -> Union[dict, None]:
    """Helper function to retrieve the LOA document application bundle from the API.

    Returns the LOA document bundle in a dict if it exists, else None"""
    client = TRSAPIClient(token=settings.HEALTH_CHECK_TOKEN)
    trs_document_bundles = client.document_bundles()

    # We've got all the TRS document bundles, let's find the LOA
    loa_document_bundle = next(
        filter(
            lambda document_bundle: document_bundle["submission_type"]
            == "Letter of Authority"
            and document_bundle["status"] == "LIVE",
            trs_document_bundles,
        ),
        None,
    )
    return loa_document_bundle


def get_uploaded_loa_document(submission: dict) -> Union[dict, None]:
    """Helper function to retrieve the LOA document uploaded by a user given a submission.

    Returns the LOA document in a dict if it exists, else None."""
    if submission_documents := submission.get("submission_documents"):
        # Getting the uploaded LOA document if it exists
        loa_document = next(
            filter(
                lambda document: document["type"]["key"] == "loa",
                submission_documents,
            ),
            None,
        )
        if loa_document:
            return loa_document
    return None


def is_phone_number_valid(country_code: str, phone_number: str) -> bool:
    """Helper function to validate a phone number given a country code and phone number.

    Returns True if the phone number is valid, else False."""
    try:
        phone_number_obj = phonenumbers.parse(phone_number, country_code)
    except phonenumbers.phonenumberutil.NumberParseException:
        return False
    if not phonenumbers.is_valid_number(phone_number_obj):
        return False
    return True
