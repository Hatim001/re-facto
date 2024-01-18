from django.test import TestCase
from django.http import HttpResponse,JsonResponse
from unittest.mock import patch, MagicMock
from account.models.account import UserAccount
from account.models.configuration import UserConfiguration
from account.models.repository import Repository
from account.proxies.github_account import GitHubAccount
from core.utils.exceptions import ValidationError
from account.views.github.config import GitHubConfigurationView
from account.models.branch import Branch
from account.models.source_configuration import SourceConfiguration
from account.models.target_configuration import TargetConfiguration

class GitHubConfigurationViewTestCase(TestCase):
    
    def setUp(self):
        user = UserAccount.objects.create(account_id=1234, access_token=" ", user_name="test")
        UserConfiguration.objects.create(user=user,commit_interval=5,max_lines=10)
        repo = Repository.objects.create(repo_id=98765,name="repo1",url="https://api.github.com/repos/test/repo1",user=user)
        branch1 = Branch.objects.create(name="main",repository=repo,user=user)
        branch2 = Branch.objects.create(name="develop",repository=repo,user=user)
        SourceConfiguration.objects.create(source_branch=branch1,repository=repo,user=user)
        SourceConfiguration.objects.create(source_branch=branch2,repository=repo,user=user)
        TargetConfiguration.objects.create(target_branch=branch1,repository=repo,user=user)
        self.view = GitHubConfigurationView()

    def create_mock_request(self, method='GET', data=None):
        request = MagicMock()
        request.method = method
        request.session = {'user_id': 1234}
        request.data = data
        return request

    @patch('account.models.branch.Branch.fetch_branches')
    def test_get_method(self,mock_fetch_branches):
        mock_request = self.create_mock_request()
        mock_fetch_branches.return_value = [ { "name": "develop" } , { "name": "main" } ]
        response = self.view.get(mock_request)
        self.assertIsInstance(response, JsonResponse)

    def test_post_method(self):
        mock_request = self.create_mock_request(method='POST', data={
            "commit_interval": 5,
            "max_lines": 30,
            "repositories": [ {  "repo_id": 98765, "name": "repo1", "url": "https://api.github.com/repos/test/repo1", "source_branches": [ { "name": "develop","is_selected": True }, { "name": "main","is_selected": True } ], "target_branches": [ { "name": "develop",  "is_selected": False },{"name": "main", "is_selected": True }]}],
        })
        response = self.view.post(mock_request)
        self.assertIsInstance(response, HttpResponse)

    def test_validate_configuration(self):
        with self.assertRaises(ValidationError):
            self.view.validate_configuration(-1, 1)
        with self.assertRaises(ValidationError):
            self.view.validate_configuration(1, -1)

    def test_configure_source_branches(self):
        user_id = 1234
        repo_id = 98765
        source_branches = [{"name": "main"}, {"name": "develop"}]
        configured_source_branches = ["main"]
        with patch.object(SourceConfiguration, 'fetch_configured_branches', return_value=configured_source_branches):
            self.view.configure_source_branches(user_id, repo_id, source_branches)
        self.assertTrue(source_branches[0].get("is_selected"))
        self.assertFalse(source_branches[1].get("is_selected"))

    def test_configure_target_branches(self):
        user_id = 1234
        repo_id = 98765
        target_branches = [{"name": "main"}, {"name": "develop"}]
        self.view.configure_target_branches(user_id, repo_id, target_branches)
        self.assertTrue(target_branches[0].get("is_selected"))
        self.assertFalse(target_branches[1].get("is_selected"))

    def test_update_source_configuration(self):
        user_id = 1234
        repo_id = 98765
        branch_name = "main"
        self.view.update_source_configuration(user_id, repo_id, branch_name)

    def test_update_target_configuration(self):
        user_id = 1234
        repo_id = 98765
        target_branch = "main"
        self.view.update_target_configuration(user_id, repo_id, target_branch)
    
    def test_cleanup_branches(self):
        user_id = 1234
        repo_id = 98765
        names = ["main"]
        self.view.cleanup_branches(user_id, repo_id, names)
