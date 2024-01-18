from django.db import models

from account.models.account import UserAccount
from account.models.branch import Branch
from account.models.configuration import UserConfiguration
from account.models.repository import Repository
from core.models.base import BaseModel


class SourceConfiguration(BaseModel):
    """Model/Manager for Source_Branch Configurations"""

    source_branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    current_commit = models.IntegerField(default=1)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    class Meta:
        db_table = "SourceConfiguration"

    @classmethod
    def configure_branch(cls, user_id, repo_id, branch_name):
        """adding a new source branch configuration for a specific repository"""
        user_instance = UserAccount.objects.get(account_id=user_id)
        repository_instance = Repository.objects.get(
            repo_id=repo_id, user=user_instance
        )
        branch, _ = Branch.objects.get_or_create(
            repository=repository_instance, name=branch_name, user=user_instance
        )
        source_configuration, _ = SourceConfiguration.objects.get_or_create(
            source_branch=branch, user=user_instance, repository=repository_instance
        )
        return source_configuration

    @classmethod
    def update_current_commit(cls, user_id, repo_id, branch_name):
        """updating the current commit number in the database by increments of one commit"""
        user_instance = UserAccount.objects.get(account_id=user_id)
        repository_instance = Repository.objects.get(
            repo_id=repo_id, user=user_instance
        )
        source_branch = Branch.objects.get(
            user=user_instance, repository=repository_instance, name=branch_name
        )
        source_configuration = SourceConfiguration.objects.get(
            user=user_instance,
            repository=repository_instance,
            source_branch=source_branch,
        )
        source_configuration.current_commit = source_configuration.current_commit + 1
        user_configuration = UserConfiguration.objects.get(user=user_instance)
        if int(source_configuration.current_commit or 0) > int(
            user_configuration.commit_interval or 0
        ):
            source_configuration.current_commit = 1
        source_configuration.save()

    @classmethod
    def fetch_configured_branches(cls, user_id, repo_id):
        """fetching configured source branches from database"""
        user_instance = UserAccount.objects.get(account_id=user_id)
        repo_instance = Repository.objects.get(repo_id=repo_id, user=user_instance)
        configs = SourceConfiguration.objects.filter(
            repository=repo_instance, user=user_instance
        )
        return [config.source_branch.name for config in configs]
