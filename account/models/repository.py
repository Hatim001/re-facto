import copy
import requests
from django.db import models

from account.models.account import UserAccount
from core.models.base import BaseModel


class Repository(BaseModel):
    """Repositories for each User"""

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    repo_id = models.BigIntegerField()
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=500)

    class Meta:
        db_table = "Repository"

    @classmethod
    def prepare_repositories(cls, user, token):
        """creating or updating repositories for a user"""
        repos = cls.fetch_repositories(token=token)
        account_id = user.get("id")
        user_instance = UserAccount.objects.get(account_id=account_id)

        for repo in repos:
            repo_id = repo.get("id")
            update_values = {
                "user": user_instance,
                "repo_id": repo_id,
                "name": repo.get("name"),
                "url": repo.get("url"),
            }
            instance = {}
            if instance := Repository.objects.filter(
                user=user_instance, repo_id=repo_id
            ).first():
                instance.set_values(update_values)
                instance.save()
            else:
                instance = Repository.objects.create(**update_values)
                instance.save()

    @classmethod
    def fetch_repositories(cls, token):
        """fetches all repositories of the user"""
        repo_api = "https://api.github.com/user/repos"
        token_payload = {
            "scope": "repo",
            "visibility": "all",
        }
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(repo_api, headers=headers, data=token_payload)
        return response.json()

    @classmethod
    def read_repositories(cls, user_id):
        """fetching repository details related to the user"""
        from account.models.branch import Branch
        user_instance = UserAccount.objects.get(account_id=user_id)
        repos = Repository.objects.filter(user=user_instance)
        all_repos_data = []
        for repo in repos:
            branches = Branch.fetch_branches(user_id, repo)
            branches_copy = copy.deepcopy(branches)
            repo_data = {
                "repo_id": repo.repo_id,
                "name": repo.name,
                "url": repo.url,
                "source_branches": branches,
                "target_branches": branches_copy,
            }
            all_repos_data.append(repo_data)
        return all_repos_data
