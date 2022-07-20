from v2_api_client.library import (submissions, users, cases)


class APIClient(
    users.UsersAPIClient,
    submissions.SubmissionsAPIClient,
    cases.CasesAPIClient
):
    pass
