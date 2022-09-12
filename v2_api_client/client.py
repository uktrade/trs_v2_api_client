from v2_api_client.library import (cases, contacts, invititations, organisations, submissions,
                                   users, documents)


class TRSAPIClient:
    def __init__(self, *args, **kwargs):
        token = kwargs.pop("token")
        super().__init__(*args, **kwargs)
        self.submissions = submissions.SubmissionsAPIClient(token=token, *args, **kwargs)
        self.users = users.UsersAPIClient(token=token, *args, **kwargs)
        self.cases = cases.CasesAPIClient(token=token, *args, **kwargs)
        self.documents = documents.DocumentsAPIClient(token=token, *args, **kwargs)
        self.document_bundles = documents.DocumentBundlesAPIClient(token=token, *args, **kwargs)
        self.invitations = invititations.InvitationsAPIClient(token=token, *args, **kwargs)
        self.organisations = organisations.OrganisationAPIClient(token=token, *args, **kwargs)
        self.contacts = contacts.ContactsAPIClient(token=token, *args, **kwargs)
        self.two_factor_auths = users.TwoFactorAuthsAPIClient(token=token, *args, **kwargs)
        self.organisation_case_roles = organisations.OrganisationCaseRoleAPIClient(
            token=token,
            *args, **kwargs
        )


"""submission_id = "!234"

client = TRSAPIClient()

submission = client.submissions.retrieve(submission_id)
submission == TRSObject()

submission.date_created = datetime.datetime.now()
submission.date_created += datetime.timedelta(days=30)

submission.save()

submission.date_created = datetime.datetime.now()
submission.save()


class MyOD(OD):
    def __setattr__(self, key, value):
        if isinstance(value, datetime.datetime):
            value = value.strftime()"""
