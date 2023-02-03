from v2_api_client.library import (
    cases,
    contacts,
    documents,
    invititations,
    organisations,
    submissions,
    users,
    generic
)


class TRSAPIClient:
    """The V2 TRS API Client.

    `Typically instantiated in middleware and exposed through the self.client object, but can be
    instantiated on its own as long as you pass a token kwarg to __init__.

    USAGE:

    The API client has a number of attributes, all relating to a specific TRS object (e.g.
    submissions). These attributes are instatiated subclasses of the BaseAPIClient class with
    specific endpoints defined relating to the TRS object in question, (e.g. /submissions).

    self.submissions({submission_id}) --> Submission object
    self.submissions() --> List of all submission objects
    self.submissions({"case": {case_id}}) --> Creates a new submission object

    The objects returned by these calls are instances of TRSObject (or a subclass).
    """

    def __init__(self, *args, **kwargs):
        token = kwargs.pop("token")
        timeout = kwargs.pop("timeout", None)
        
        super().__init__(*args, **kwargs)
        self.submissions = submissions.SubmissionsAPIClient(
            token=token,
            timeout=timeout,
            *args,
            **kwargs
        )
        self.users = users.UsersAPIClient(
            token=token, 
            timeout=timeout, 
            *args, 
            **kwargs
        )
        self.cases = cases.CasesAPIClient(
            token=token, 
            timeout=timeout, 
            *args, 
            **kwargs
        )
        self.documents = documents.DocumentsAPIClient(
            token=token, 
            timeout=timeout, 
            *args, 
            **kwargs
        )
        self.document_bundles = documents.DocumentBundlesAPIClient(
            token=token, 
            timeout=timeout, 
            *args, 
            **kwargs
        )
        self.invitations = invititations.InvitationsAPIClient(
            token=token, 
            timeout=timeout, 
            *args, 
            **kwargs
        )
        self.organisations = organisations.OrganisationAPIClient(
            token=token, 
            timeout=timeout, 
            *args, 
            **kwargs
        )
        self.contacts = contacts.ContactsAPIClient(
            token=token, 
            timeout=timeout, 
            *args, 
            **kwargs
        )
        self.case_contacts = contacts.CaseContactsAPIClient(
            token=token, 
            timeout=timeout, 
            *args, 
            **kwargs
        )
        self.two_factor_auths = users.TwoFactorAuthsAPIClient(
            token=token, 
            timeout=timeout, 
            *args, 
            **kwargs
        )
        self.feature_flags = generic.FeatureFlagsAPIClient(
            token=token, 
            timeout=timeout, 
            *args, 
            **kwargs
        )
        self.feedback = generic.FeedbackAPIClient(
            token=token, 
            timeout=timeout, 
            *args, 
            **kwargs
        )
        self.organisation_case_roles = organisations.OrganisationCaseRoleAPIClient(
            token=token, 
            timeout=timeout, 
            *args, 
            **kwargs
        )
        self.organisation_merge_records = organisations.OrganisationMergeRecordAPIClient(
            token=token,
            timeout=timeout,
            *args,
            **kwargs
        )
        self.duplicate_organisation_merges = organisations.DuplicateOrganisationMergeAPIClient(
            token=token,
            timeout=timeout,
            *args,
            **kwargs
        )
        self.submission_organisation_merge_records = submissions.SubmissionOrganisationMergeRecordAPIClient(
            token=token,
            timeout=timeout,
            *args,
            **kwargs
        )
        self.user_profiles = users.UserProfileAPIClient(
            token=token,
            timeout=timeout,
            *args,
            **kwargs
        )
