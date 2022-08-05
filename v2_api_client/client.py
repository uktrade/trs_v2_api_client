from v2_api_client.library import (submissions, users, cases, documents)


class APIClient(
    users.UsersAPIClient,
    submissions.SubmissionsAPIClient,
    cases.CasesAPIClient,
    documents.DocumentsAPIClient
):
    pass
