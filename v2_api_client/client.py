import datetime

from v2_api_client.library import (
    cases,
    documents,
    submissions,
    users,
    invititations,
    organisations
)


class TRSAPIClient:
    def __init__(self, *args, **kwargs):
        token = kwargs.pop("token")
        super().__init__(*args, **kwargs)
        self.submissions = submissions.SubmissionsAPIClient(token=token, *args, **kwargs)
        self.users = users.UsersAPIClient(token=token, *args, **kwargs)
        self.cases = cases.CasesAPIClient(token=token, *args, **kwargs)
        self.documents = documents.DocumentsAPIClient(token=token, *args, **kwargs)
        self.invitations = invititations.InvitationsAPIClient(token=token, *args, **kwargs)
        self.organisations = organisations.OrganisationAPIClient(token=token, *args, **kwargs)


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

