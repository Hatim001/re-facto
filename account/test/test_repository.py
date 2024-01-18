import json
from unittest.mock import ANY, MagicMock, patch

from django.test import TestCase

from account.models import Repository
from account.models.account import GITHUB, GITLAB, UserAccount


class RepositoryTestCase(TestCase):
    def setUp(self):
        self.user_account = UserAccount.objects.create(
            account_id="123456",
            access_token="abcdef",
            email="test@example.com",
            account_type=GITHUB,
            user_name="testuser",
            name="Test User",
            company="Test Company",
        )

    @patch("requests.get")
    def test_prepare_repositories(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "name": "repo1",
                "url": "https://api.github.com/repos/testuser/repo1",
            },
            {
                "id": 2,
                "name": "repo2",
                "url": "https://api.github.com/repos/testuser/repo2",
            },
        ]
        mock_requests_get.return_value = mock_response
        Repository.prepare_repositories(user={"id": "123456"}, token="abcdef")
        self.assertEqual(Repository.objects.count(), 2)
        self.assertTrue(Repository.objects.filter(repo_id=1, name="repo1").exists())
        self.assertTrue(Repository.objects.filter(repo_id=2, name="repo2").exists())
        expected_url = "https://api.github.com/user/repos"
        expected_headers = {
            "Accept": "application/json",
            "Authorization": "Bearer abcdef",
        }
        data = {"scope": "repo", "visibility": "all"}
        mock_requests_get.assert_called_once_with(
            expected_url, headers=expected_headers, data=data
        )

    @patch("requests.get")
    def test_fetch_repositories(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "name": "repo1",
                "url": "https://api.github.com/repos/testuser/repo1",
            },
            {
                "id": 2,
                "name": "repo2",
                "url": "https://api.github.com/repos/testuser/repo2",
            },
        ]
        mock_requests_get.return_value = mock_response
        repositories = Repository.fetch_repositories(token="abcdef")
        self.assertEqual(len(repositories), 2)
        self.assertEqual(repositories[0]["id"], 1)
        self.assertEqual(repositories[1]["id"], 2)
        expected_url = "https://api.github.com/user/repos"
        expected_headers = {
            "Accept": "application/json",
            "Authorization": "Bearer abcdef",
        }
        data = {"scope": "repo", "visibility": "all"}
        mock_requests_get.assert_called_once_with(
            expected_url, headers=expected_headers, data=data
        )
