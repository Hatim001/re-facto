from django.conf import settings
from django.http import HttpRequest
from django.test import Client, TestCase, RequestFactory
from account.models.account import UserAccount
from core.utils.exceptions import ValidationError
from unittest.mock import patch, MagicMock
from account.proxies.github_account import GitHubAccount
from account.serializers.serializer import UserAccountSerializer
from account.models.repository import Repository
from account.models.configuration import UserConfiguration


class GitHubAccountTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.email = "test@test.com"
        self.company = "Test Co"

    @patch('requests.post')
    def test_fetch_access_token(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = mock_response

        oauth_code = "test_code"
        result = GitHubAccount.fetch_access_token(oauth_code)
        self.assertEqual(result, "test_token")
        mock_post.assert_called_once_with(
            url=GitHubAccount.ACCESS_TOKEN_URL,
            headers={"Accept": "application/json", "scope": "repo"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_APP_SECRET,
                "code": oauth_code,
            }
        )

    def test_fetch_access_token_no_code(self):
        with self.assertRaises(ValidationError):
            GitHubAccount.fetch_access_token(None)

    @patch('requests.get')
    def test_fetch_user_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"user_data": "test_data"}
        mock_get.return_value = mock_response

        access_token = "test_token"
        result = GitHubAccount.fetch_user_data(access_token)
        self.assertEqual(result, {"user_data": "test_data"})
        mock_get.assert_called_once_with(
            url="https://api.github.com/user",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
        )

    @patch('account.models.configuration.UserConfiguration.objects.create')
    def test_prepare_configurations(self, mock_create):
        user_id = 1
        GitHubAccount.prepare_configurations(user_id)
        mock_create.assert_called_once_with(
            user_id=user_id, commit_interval=5, max_lines=30
        )

    @patch('account.models.account.UserAccount.objects.filter')
    @patch('account.models.account.UserAccount.objects.create')
    def test_create_account_new(self, mock_create, mock_filter):
        mock_filter.return_value.first.return_value = None
        user_data = {
            "account_id": 1,
            "access_token": "test_token",
            "email": self.email,
            "login": "test",
            "name": "Test",
            "company": self.company
        }
        UserAccount.objects.create(**user_data)
        mock_create.assert_called_once_with(**user_data)

    @patch('account.models.account.UserAccount.objects.filter')
    def test_create_account_existing(self, mock_filter):
        mock_instance = MagicMock()
        mock_filter.return_value.first.return_value = mock_instance
        user_data = {
            "id": 1,
            "email": self.email,
            "login": "test",
            "name": "Test",
            "company": self.company
        }
        access_token = "test_token"
        GitHubAccount.create_account(user_data, access_token)
        mock_instance.set_values.assert_called_once_with(
            {
                "account_id": user_data["id"],
                "access_token": access_token,
                "email": user_data["email"],
                "user_name": user_data["login"],
                "name": user_data["name"],
                "company": user_data["company"],
                "account_type": "GitHub",
            }
        )
        mock_instance.save.assert_called_once()

    @patch('django.middleware.csrf.rotate_token')
    @patch('account.models.account.UserAccount.objects.get')
    def test_prepare_session(self, mock_rotate_token, mock_get):
        user_data = {
            "id": 1,
            "email": self.email,
            "login": "test",
            "name": "Test",
            "company": self.company,
            "avatar_url": "xyz.png"
        }
        user_instance = UserAccount.objects.create(account_id=user_data["id"])
        mock_get.return_value = user_instance

        client = Client()
        response = client.get("/")
        request = response.wsgi_request
        
        request.session.update({
            "isLoggedIn": True,
            "user_id": user_data["id"],
            "user": UserAccountSerializer(user_instance).data,
            "avatar_url": user_data["avatar_url"]
        })

        request.session.set_expiry(settings.SESSION_EXPIRY)
        self.assertTrue(request.session["isLoggedIn"])
        self.assertEqual(request.session["user_id"], user_data["id"])
        self.assertEqual(request.session["user"], UserAccountSerializer(user_instance).data)
        self.assertEqual(request.session["avatar_url"], user_data["avatar_url"])
        self.assertEqual(request.session.get_expiry_age(), settings.SESSION_EXPIRY)

    @patch('account.models.account.UserAccount.objects.get')
    @patch('account.models.repository.Repository.objects.filter')
    @patch('account.models.branch.Branch.fetch_branches')
    def test_fetch_repositories(self, mock_fetch_branches, mock_filter, mock_get):
        user_id = 1
        user_instance = MagicMock()
        mock_get.return_value = user_instance

        repo_instance = MagicMock()
        repo_instance.repo_id = 1
        repo_instance.name = "test_repo"
        repo_instance.url = "https://github.com/test/repo"
        mock_filter.return_value = [repo_instance]

        branches = [{"name": "branch1"}, {"name": "branch2"}]
        mock_fetch_branches.side_effect = [branches, branches]

        result = Repository.read_repositories(user_id)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["repo_id"], repo_instance.repo_id)
        self.assertEqual(result[0]["name"], repo_instance.name)
        self.assertEqual(result[0]["url"], repo_instance.url)
        self.assertEqual(result[0]["source_branches"], branches)
        self.assertEqual(result[0]["target_branches"], branches)

        mock_get.assert_called_once_with(account_id=user_id)
        mock_filter.assert_called_once_with(user=user_instance)
        mock_fetch_branches.assert_called_with(user_id, repo_instance)

    @patch('account.models.account.UserAccount.objects.get')
    @patch('account.models.configuration.UserConfiguration.objects.get')
    @patch('account.models.repository.Repository.objects.filter')
    @patch('account.models.source_configuration.SourceConfiguration.objects.filter')
    @patch('account.models.target_configuration.TargetConfiguration.objects.get')
    def test_fetch_configurations(
        self, mock_get_target, mock_filter_source, mock_filter_repo,
        mock_get_config, mock_get_user
    ):
        user_id = 1
        user_instance = MagicMock()
        mock_get_user.return_value = user_instance

        config_instance = MagicMock()
        config_instance.commit_interval = 5
        config_instance.max_lines = 30
        mock_get_config.return_value = config_instance

        repo_instance = MagicMock()
        repo_instance.repo_id = 1
        repo_instance.name = "test_repo"
        repo_instance.url = "https://github.com/test/repo"
        mock_filter_repo.return_value = [repo_instance]

        source_config_instance = MagicMock()
        source_config_instance.source_branch.name = "branch1"
        source_config_instance.current_commit = "commit1"
        mock_filter_source.return_value = [source_config_instance]

        target_config_instance = MagicMock()
        target_config_instance.target_branch.name = "branch2"
        mock_get_target.return_value = target_config_instance

        result = UserConfiguration.fetch_configurations(user_id)
        self.assertEqual(result["user_id"], user_id)
        self.assertEqual(result["commit_interval"], config_instance.commit_interval)
        self.assertEqual(result["max_lines"], config_instance.max_lines)
        self.assertEqual(len(result["repositories"]), 1)
        self.assertEqual(result["repositories"][0]["repo_id"], repo_instance.repo_id)
        self.assertEqual(result["repositories"][0]["name"], repo_instance.name)
        self.assertEqual(result["repositories"][0]["url"], repo_instance.url)
        self.assertEqual(len(result["repositories"][0]["source_branches"]), 1)
        self.assertEqual(result["repositories"][0]["source_branches"][0]["name"], "branch1")
        self.assertEqual(result["repositories"][0]["source_branches"][0]["commit_number"], "commit1")
        self.assertEqual(result["repositories"][0]["target_branch"], "branch2")

        mock_get_user.assert_called_once_with(account_id=user_id)
        mock_get_config.assert_called_once_with(user=user_instance)
        mock_filter_repo.assert_called_once_with(user=user_instance)
        mock_filter_source.assert_called_once_with(repository=repo_instance, user=user_instance)
        mock_get_target.assert_called_once_with(user=user_instance, repository=repo_instance)

    @patch('account.proxies.github_account.GitHubAccount.fetch_access_token')
    @patch('account.proxies.github_account.GitHubAccount.fetch_user_data')
    @patch('account.proxies.github_account.GitHubAccount.create_account')
    @patch('account.models.repository.Repository.prepare_repositories')
    @patch('account.proxies.github_account.GitHubAccount.prepare_session')
    def test_authorize(
        self, mock_prepare_session, mock_prepare_repositories,
        mock_create_account, mock_fetch_user_data, mock_fetch_access_token
    ):
        oauth_code = "test_code"
        request = self.factory.get("/")

        access_token = "test_token"
        user_data = {"id": 1, "email": self.email, "login": "test", "name": "Test", "company": self.company}

        mock_fetch_access_token.return_value = access_token
        mock_fetch_user_data.return_value = user_data

        GitHubAccount.authorize(oauth_code, request)

        mock_fetch_access_token.assert_called_once_with(oauth_code=oauth_code)
        mock_fetch_user_data.assert_called_once_with(access_token=access_token)
        mock_create_account.assert_called_once_with(user_data=user_data, access_token=access_token)
        mock_prepare_repositories.assert_called_once_with(user=user_data, token=access_token)
        mock_prepare_session.assert_called_once_with(request=request, user_data=user_data)