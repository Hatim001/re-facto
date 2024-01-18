from unittest.mock import patch, MagicMock
from django.test import TestCase
from datetime import datetime

from service.models.github.bot import GithubBot 
from service.models.github.event import GithubEvent
from github import Branch, Github, InputGitTreeElement
from account.models.source_configuration import SourceConfiguration

class BotTestCase(TestCase):
    def setUp(self):
        self.description = 'Second repository'
        self.url = 'https://github.com/username/repo2'
        self.bot = GithubBot(request=MagicMock(), is_event=True)
        self.bot.event = MagicMock()
        self.bot.github = MagicMock()
        self.bot.event.headers = {"X-GitHub-Event": "push"}
        self.bot.repo = self.bot.github.get_user().get_repo.return_value


    @patch('requests.get')
    def test_get_commit(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'commit_info': 'sample_commit_data'}
        mock_requests_get.return_value = mock_response

        owner = 'owner'
        repo = 'repo'
        commit_id = 'commit_id'
        commit_info = self.bot.get_commit(owner, repo, commit_id)

        mock_requests_get.assert_called_once_with(url=f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_id}")
        self.assertEqual(commit_info, {'commit_info': 'sample_commit_data'})
    
    @patch('requests.get')
    def test_get_commit(self, mock_requests_get):
        bot = GithubBot()

        owner = 'username'
        repo = 'repository'
        commit_id = '1234567890'

        mock_response = MagicMock()
        mock_response.json.return_value = {
            'commit_info_key': 'commit_info_value',
        }
        mock_requests_get.return_value = mock_response

        result = bot.get_commit(owner, repo, commit_id)

        expected_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_id}"
        mock_requests_get.assert_called_once_with(url=expected_url)
        self.assertEqual(result, mock_response.json())

    def test_execute_event_push(self):
        self.bot.event.type = "push"
        self.bot.refactor = MagicMock()

        self.bot.execute_event()

        self.bot.refactor.assert_called_once()

    def test_execute_event_other(self):
        self.bot.event.type = "other_event_type"
        self.bot.refactor = MagicMock()

        self.bot.execute_event()

        self.bot.refactor.assert_not_called()

    def test_get_repo_details_found(self):
        repo_list = [
            {
                'repo_id': 1,
                'name': 'repo1',
                'description': 'First repository',
                'url': 'https://github.com/username/repo1',
                'source_branches': [
                    {'name': 'main', 'commit_number': 15},
                    {'name': 'feature_branch', 'commit_number': 8},
                    # Add more branches or modify details as needed
                ],
                'target_branch': 'master'
            },
            {
                'repo_id': 2,
                'name': 'repo2',
                'description': self.description,
                'url': self.url,
                'source_branches': [
                    {'name': 'main', 'commit_number': 20},
                    {'name': 'bugfix_branch', 'commit_number': 10},
                    # Add more branches or modify details as needed
                ],
                'target_branch': 'main'
            },
        ]
        name = 'repo2'

        result = self.bot.get_repo_details(repo_list, name)

        expected_result = {
            'name': 'repo2',
            'description': self.description,
            'repo_id': 2,
            'source_branches': [
                {'name': 'main', 'commit_number': 20},
                {'name': 'bugfix_branch', 'commit_number': 10},
            ],
            'target_branch': 'main',
            'url': self.url
        }
        self.assertEqual(result, expected_result)

    def test_get_repo_details_not_found(self):
        
        repo_list = [
            {
                'repo_id': 1,
                'name': 'repo1',
                'description': 'First repository',
                'url': 'https://github.com/username/repo1',
                'source_branches': [
                    {'name': 'main', 'commit_number': 15},
                    {'name': 'feature_branch', 'commit_number': 8},
                    # Add more branches or modify details as needed
                ],
                'target_branch': 'master'
            },
            {
                'repo_id': 2,
                'name': 'repo2',
                'description': self.description,
                'url': self.url,
                'source_branches': [
                    {'name': 'main', 'commit_number': 20},
                    {'name': 'bugfix_branch', 'commit_number': 10},
                    # Add more branches or modify details as needed
                ],
                'target_branch': 'main'
            },
        ]
        name = 'repo3' 

        result = self.bot.get_repo_details(repo_list, name)

        self.assertIsNone(result)

    def test_get_branch_details_found(self):
        branch_list = [
            {"name": "main", "commit_number": 10},
            {"name": "feature_branch", "commit_number": 5},
        ]

        branch_name = "main"

        result = self.bot.get_branch_details(branch_list, branch_name)

        expected_result = {"name": "main", "commit_number": 10}

        self.assertEqual(result, expected_result)

    def test_get_branch_details_not_found(self):
        branch_list = [
            {"name": "main", "commit_number": 10},
            {"name": "feature_branch", "commit_number": 5},
        ]

        branch_name = "non_existent_branch"

        result = self.bot.get_branch_details(branch_list, branch_name)

        self.assertIsNone(result)