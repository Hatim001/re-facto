from django.test import TestCase

from account.models import TargetConfiguration
from account.models.account import GITHUB, GITLAB, UserAccount
from account.models.branch import Branch
from account.models.repository import Repository


class TargetConfigurationTestCase(TestCase):
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

    def test_add_configuration(self):
        TargetConfiguration.add_configuration(
            user_id=self.user_account.account_id,
            repo_id=self.repository.repo_id,
            target_branch="feature-1",
        )
        added_configuration = TargetConfiguration.objects.get(
            user=self.user_account, repository=self.repository
        )
        self.assertIsNotNone(added_configuration.target_branch)
        self.assertEqual(added_configuration.target_branch.name, "feature-1")

    def test_fetch_configuration(self):
        non_existing_configuration = TargetConfiguration.fetch_configuration(
            user_id=self.user_account.account_id, repo_id=self.repository.repo_id
        )
        self.assertIsNone(non_existing_configuration)
        TargetConfiguration.add_configuration(
            user_id=self.user_account.account_id,
            repo_id=self.repository.repo_id,
            target_branch="feature-2",
        )
        existing_configuration = TargetConfiguration.fetch_configuration(
            user_id=self.user_account.account_id, repo_id=self.repository.repo_id
        )
        self.assertIsNotNone(existing_configuration)
        self.assertEqual(existing_configuration.name, "feature-2")
