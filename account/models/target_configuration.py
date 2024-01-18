from django.db import models

from account.models.account import UserAccount
from account.models.branch import Branch
from account.models.repository import Repository
from core.models.base import BaseModel


class TargetConfiguration(BaseModel):
    """Model/Manager for Target_Branch Configurations"""

    target_branch = models.ForeignKey(
        Branch,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="target_branch",
    )
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)

    class Meta:
        db_table = "TargetConfiguration"

    @classmethod
    def add_configuration(cls, user_id, repo_id, target_branch):
        """adding or updating target branch in a repository"""
        user_account = UserAccount.objects.get(account_id=user_id)
        repo = Repository.objects.get(repo_id=repo_id, user=user_account)
        branch, _ = Branch.objects.get_or_create(
            repository=repo, name=target_branch, user=user_account
        )
        target_configuration, _ = TargetConfiguration.objects.get_or_create(
            user=user_account, repository=repo
        )
        target_configuration.target_branch = branch
        target_configuration.save()

    @classmethod
    def fetch_configuration(cls, user_id, repo_id):
        """fetching target branch in a repository configuration"""
        user_instance = UserAccount.objects.get(account_id=user_id)
        repo_instance = Repository.objects.get(repo_id=repo_id, user=user_instance)
        # checking if configuration is set or not
        try:
            target_configuration = TargetConfiguration.objects.get(
                user=user_instance, repository=repo_instance
            )
            return target_configuration.target_branch
        except TargetConfiguration.DoesNotExist:
            return None
