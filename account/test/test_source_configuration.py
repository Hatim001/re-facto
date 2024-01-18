from django.test import TestCase
from account.models.source_configuration import SourceConfiguration
from account.models.account import UserAccount
from account.models.repository import Repository
from account.models.branch import Branch
from account.models.configuration import UserConfiguration
from unittest.mock import patch, MagicMock


class SourceConfigurationTest(TestCase):
    def setUp(self):
        self.user_id = 1
        self.repo_id = 1
        self.branch_name = "test_branch"

    @patch("account.models.account.UserAccount.objects.get")
    @patch("account.models.repository.Repository.objects.get")
    @patch("account.models.branch.Branch.objects.get_or_create")
    @patch(
        "account.models.source_configuration.SourceConfiguration.objects.get_or_create"
    )
    def test_configure_branch(
        self,
        mock_get_or_create,
        mock_branch_get_or_create,
        mock_repo_get,
        mock_user_get,
    ):
        user_instance = MagicMock()
        repo_instance = MagicMock()
        branch_instance = MagicMock()
        source_config_instance = MagicMock()

        mock_user_get.return_value = user_instance
        mock_repo_get.return_value = repo_instance
        mock_branch_get_or_create.return_value = (branch_instance, True)
        mock_get_or_create.return_value = (source_config_instance, True)

        result = SourceConfiguration.configure_branch(
            self.user_id, self.repo_id, self.branch_name
        )

        mock_user_get.assert_called_once_with(account_id=self.user_id)
        mock_repo_get.assert_called_once_with(repo_id=self.repo_id, user=user_instance)
        mock_branch_get_or_create.assert_called_once_with(
            repository=repo_instance, name=self.branch_name, user=user_instance
        )
        mock_get_or_create.assert_called_once_with(
            source_branch=branch_instance, user=user_instance, repository=repo_instance
        )

        self.assertEqual(result, source_config_instance)

    @patch("account.models.account.UserAccount.objects.get")
    @patch("account.models.repository.Repository.objects.get")
    @patch("account.models.branch.Branch.objects.get")
    @patch("account.models.source_configuration.SourceConfiguration.objects.get")
    @patch("account.models.configuration.UserConfiguration.objects.get")
    def test_update_current_commit(
        self,
        mock_user_config_get,
        mock_source_config_get,
        mock_branch_get,
        mock_repo_get,
        mock_user_get,
    ):
        user_instance = MagicMock()
        repo_instance = MagicMock()
        branch_instance = MagicMock()
        source_config_instance = MagicMock()
        user_config_instance = MagicMock()

        mock_user_get.return_value = user_instance
        mock_repo_get.return_value = repo_instance
        mock_branch_get.return_value = branch_instance
        mock_source_config_get.return_value = source_config_instance
        mock_user_config_get.return_value = user_config_instance

        SourceConfiguration.update_current_commit(
            user_id=self.user_id, repo_id=self.repo_id, branch_name=self.branch_name
        )

        mock_user_get.assert_called_once_with(account_id=self.user_id)
        mock_repo_get.assert_called_once_with(repo_id=self.repo_id, user=user_instance)
        mock_branch_get.assert_called_once_with(
            user=user_instance, repository=repo_instance, name=self.branch_name
        )
        mock_source_config_get.assert_called_once_with(
            user=user_instance, repository=repo_instance, source_branch=branch_instance
        )
        mock_user_config_get.assert_called_once_with(user=user_instance)

        source_config_instance.save.assert_called_once()

    @patch("account.models.account.UserAccount.objects.get")
    @patch("account.models.repository.Repository.objects.get")
    @patch("account.models.source_configuration.SourceConfiguration.objects.filter")
    def test_fetch_configured_branches(self, mock_filter, mock_repo_get, mock_user_get):
        user_instance = MagicMock()
        repo_instance = MagicMock()
        source_config_instance = MagicMock()

        mock_user_get.return_value = user_instance
        mock_repo_get.return_value = repo_instance
        mock_filter.return_value = [source_config_instance]

        result = SourceConfiguration.fetch_configured_branches(
            self.user_id, self.repo_id
        )

        mock_user_get.assert_called_once_with(account_id=self.user_id)
        mock_repo_get.assert_called_once_with(repo_id=self.repo_id, user=user_instance)
        mock_filter.assert_called_once_with(
            repository=repo_instance, user=user_instance
        )

        self.assertEqual(result, [source_config_instance.source_branch.name])
