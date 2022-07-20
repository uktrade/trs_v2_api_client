from v2_api_client.library import BaseAPIClient


class SubmissionsAPIClient(BaseAPIClient):
    def get_submissions(self, submission_type=None):
        return self.get(self.url("submissions", submission_type=submission_type))

    def get_submission(self, submission_id):
        return self.get(self.url(f"submissions/{submission_id}"))

    def create_submission(self, **kwargs):
        return self.post(self.url("submissions"), data=kwargs)

    def update_submission_status(self, submission_id, new_status):
        return self.put(self.url(f"submissions/{submission_id}/update_submission_status"), data={
            "new_status": new_status
        })
