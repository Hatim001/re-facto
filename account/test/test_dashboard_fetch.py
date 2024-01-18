import json
from unittest import mock
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from account.models.account import UserAccount
from account.models.pull_details import PullDetails
from account.proxies.dashboard_fetch import DashBoardFetch


class DashBoardFetchTests(TestCase):
    def setUp(self):
        # Setting up initial data for testing
        self.title = "Test Pull Request"
        self.commit_message = "Commit message"
        self.date = "2023-01-01T00:00:00Z"
        self.repo_name = "test_user/test_repo"
        self.user_account = UserAccount.objects.create(
            user_name="test_user",
            access_token="test_token",
        )
        self.pull_request = PullDetails.objects.create(
            author=self.user_account,
            Repo_name="test_repo",
            pull_id=1,
            title=self.title,
        )

    @mock.patch("requests.get")
    def test_get_pull_requests_status(self, mock_get):
        # Mocking the response for the 'get_pull_requests_status' method
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "head": {"ref": "test_branch"},
            "base": {"ref": "master"},
            "state": "open",
            "additions": 10,
            "deletions": 5,
            "comments": 3,
        }
        mock_get.return_value = mock_response
        pull_requests_data = [{"Repo_name": "test_repo", "pull_id": 123}]
        result = DashBoardFetch.get_pull_requests_status(pull_requests_data)
        expected_result = [
            {
                "Repo_name": "test_repo",
                "pull_id": 123,
                "source_branch": "test_branch",
                "target_branch": "master",
                "state": "open",
                "additions": 10,
                "deletions": 5,
                "comments_count": 3,
            }
        ]
        return self.assertEqual(result, expected_result)

    def test_fetch_pr_details(self):
        # Testing the 'fetch_pr_details' method
        with patch(
            "account.proxies.dashboard_fetch.DashBoardFetch.get_pull_requests_status"
        ) as mock_status:
            mock_status.return_value = [
                {"Repo_name": "test_repo", "pull_id": 1, "state": "open"}
            ]
            result = DashBoardFetch.fetch_pr_details(username="test_user")
            mock_status.assert_called_once_with(
                [
                    {
                        "Repo_name": "test_repo",
                        "pull_id": 1,
                        "author": "test_user",
                        "title": self.title,
                    }
                ]
            )
            expected_result = [
                {"Repo_name": "test_repo", "pull_id": 1, "state": "open"}
            ]
            self.assertEqual(result, expected_result)

    @patch("account.proxies.dashboard_fetch.requests.get")
    def test_get_pull_request_commits(self, mock_requests_get):
        # Testing the 'get_pull_request_commits' method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"sha": "abc123", "commit": {"message": self.commit_message}}
        ]
        mock_requests_get.return_value = mock_response
        result = DashBoardFetch.get_pull_request_commits("test_repo", 1, "test_token")
        mock_requests_get.assert_called_once_with(
            "test_repo/pulls/1/commits", headers={"Authorization": "token test_token"}
        )
        expected_result = [{"sha": "abc123", "commit": {"message": self.commit_message}}]
        self.assertEqual(result, expected_result)

    def test_extract_commit_details(self):
        # Testing the 'extract_commit_details' method
        mock_commit = {
            "sha": "abc123",
            "commit": {
                "message": self.commit_message,
                "author": {"name": "Author"},
                "committer": {"date": self.date},
            },
            "url": "https://api.github.com/repos/test_user/test_repo/commits/abc123",
        }
        user_account_instance = MagicMock()
        user_account_instance.user_name = "test_user"
        pull_request_number = 1
        result = DashBoardFetch.extract_commit_details(
            mock_commit, user_account_instance,pull_request_number
        )
        expected_result = {
            "sha": "abc123",
            "message": self.commit_message,
            "author_name": "Author",
            "date": None,
            "Repo_name": self.repo_name,
            "pull_id": 1,
        }
        self.assertEqual(result, expected_result)

    @patch("account.proxies.dashboard_fetch.DashBoardFetch.get_pull_request_commits")
    def test_fetch_branch(self, mock_get_pull_request_commits):
        # Testing the 'fetch_branch' method
        mock_get_pull_request_commits.return_value = [
            {
                "sha": "abc123",
                "commit": {
                    "message": self.commit_message,
                    "author": {"name": "Author"},
                    "committer": {"date": self.date},
                },
                "url": "https://api.github.com/repos/test_user/test_repo/commits/abc123",
            }
        ]
        result = DashBoardFetch.fetch_branch(self.user_account)
        mock_get_pull_request_commits.assert_called_once_with(
            "test_repo", 1, "test_token"
        )
        expected_result = [
            {
                "pull_id" : 1,
                "sha": "abc123",
                "message": self.commit_message,
                "author_name": "Author",
                "date": None,
                "Repo_name": self.repo_name,
            }
        ]
        self.assertEqual(result, expected_result)

    @mock.patch("account.proxies.dashboard_fetch.DashBoardFetch.fetch_branch")
    @mock.patch("account.proxies.dashboard_fetch.DashBoardFetch.fetch_pr_details")
    def test_fetch_dashboard_data(self, mock_fetch_pr_details, mock_fetch_branch):
        # Testing the 'fetch_dashboard_data' method
        # Set up mock results for fetch_branch and fetch_pr_details
        mock_fetch_branch.return_value = [
            {
                "sha": "abc123",
                "message": self.commit_message,
                "author_name": "Author",
                "date": self.date,
                "Repo_name": self.repo_name,
            }
        ]
        mock_fetch_pr_details.return_value = [
            {
                "Repo_name": "test_repo",
                "pull_id": 1,
                "author": "test_user",
                "title": self.title,
                "source_branch": "feature-branch",
                "target_branch": "main",
                "state": "open",
                "additions": 10,
                "deletions": 5,
                "comments_count": 3,
            }
        ]

        # Set up a mock request
        request = RequestFactory().get("/dashboard/")
        request.session = {"user_id": self.user_account.account_id}

        # Call the fetch_dashboard_data method
        result = DashBoardFetch.fetch_dashboard_data(request)

        # Assert that fetch_branch and fetch_pr_details were called with the correct arguments
        mock_fetch_branch.assert_called_once_with(user_account_instance=self.user_account)
        mock_fetch_pr_details.assert_called_once_with(
            username=self.user_account.user_name
        )

        # Assert that the result matches the expected output
        expected_result = {
            "json_branch_data": [
                {
                    "sha": "abc123",
                    "message": self.commit_message,
                    "author_name": "Author",
                    "date": self.date,
                    "Repo_name": self.repo_name,
                }
            ],
            "json_pr_data": [
                {
                    "Repo_name": "test_repo",
                    "pull_id": 1,
                    "author": "test_user",
                    "title": self.title,
                    "source_branch": "feature-branch",
                    "target_branch": "main",
                    "state": "open",
                    "additions": 10,
                    "deletions": 5,
                    "comments_count": 3,
                }
            ],
        }
        self.assertEqual(result, expected_result)
