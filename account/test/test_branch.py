import json
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse

from account.models import Branch
from account.models.account import GITHUB, GITLAB, UserAccount
from account.models.repository import Repository


class BranchTestCase(TestCase):
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
        self.repository = Repository.objects.create(
            repo_id="789012",
            name="testrepo",
            url="https://api.github.com/repos/testuser/testrepo",
            user=self.user_account,
        )

    @patch("requests.get")
    def test_fetch_branches(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "main"},
            {"name": "feature-1"},
            {"name": "refacto-start-1"},
            {"name": "refacto-start-2"},
        ]
        mock_requests_get.return_value = mock_response
        branches = Branch.fetch_branches(
            user_id=self.user_account.account_id, repo=self.repository
        )
        self.assertEqual(branches[0]["name"], "main")
        self.assertEqual(branches[1]["name"], "feature-1")
        expected_url = "https://api.github.com/repos/testuser/testrepo/branches"
        expected_headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.user_account.access_token}",
        }
        mock_requests_get.assert_called_once_with(
            expected_url, headers=expected_headers
        )

    def test_cleanup(self):
        Branch.objects.create(
            name="branch1", user=self.user_account, repository=self.repository
        )
        Branch.objects.create(
            name="branch2", user=self.user_account, repository=self.repository
        )
        Branch.cleanup(
            user_id=self.user_account.account_id,
            names=["branch1"],
            repo_id=self.repository.repo_id,
        )
        self.assertTrue(Branch.objects.filter(name="branch1").exists())
        self.assertFalse(Branch.objects.filter(name="branch2").exists())
