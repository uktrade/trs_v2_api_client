import datetime

from v2_api_client.library import (cases, documents, submissions, users)


class TRSAPIClient:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submissions = submissions.SubmissionsAPIClient()
        self.users = users.UsersAPIClient()
        self.cases = cases.CasesAPIClient()
        self.documents = documents.DocumentsAPIClient()


submission_id = "!234"

client = TRSAPIClient()

submission = client.submissions.retrieve(submission_id)
submission.date_created = datetime.datetime.now()
submission.save()
