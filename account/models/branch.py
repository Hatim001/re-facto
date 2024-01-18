import requests
from django.db import models
from django.db.models import Q

from account.models.account import UserAccount
from account.models.repository import Repository
from core.models.base import BaseModel


class Branch(BaseModel):
    """Model/Manager for Branches"""

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)

    class Meta:
        db_table = "Branch"

    @classmethod
    def fetch_branches(cls, user_id, repo):
        """fetching all branches in a repository"""
        api_url = repo.url + "/branches"
        user_instance = UserAccount.objects.get(account_id=user_id)
        token = user_instance.access_token
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(api_url, headers=headers)
        branches_data = response.json()
        filtered_branches = []
        for branch in branches_data:
            if isinstance(branch, dict) and "name" in branch and isinstance(branch["name"], str):
                if not branch["name"].__contains__("refactored-by-re-facto"):
                    filtered_branches.append({"name": branch["name"], "is_selected": False})

        return filtered_branches

    @classmethod
    def cleanup(cls, user_id, names, repo_id):
        """deleting the branches that are not configured as source or target"""
        user_instance = UserAccount.objects.get(account_id=user_id)
        repository_instance = Repository.objects.get(
            repo_id=repo_id, user=user_instance
        )
        branches_to_delete = Branch.objects.filter(
            ~Q(name__in=names), user=user_instance, repository=repository_instance
        )
        # Delete the fetched branches
        branches_to_delete.delete()
