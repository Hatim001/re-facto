from django.db import models
from django.utils import timezone

from account.models.account import UserAccount
from core.models.base import BaseModel


class UserConfiguration(BaseModel):
    """Model/Manager for service configurations"""

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    commit_interval = models.IntegerField()
    max_lines = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "UserConfiguration"

    @classmethod
    def update_configuration(cls, user_id, commit_interval, max_lines):
        """updating the user specific configurations like max_lines and commit_interval"""
        user_account = UserAccount.objects.get(account_id=user_id)
        user_configuration = UserConfiguration.objects.get(user=user_account)
        user_configuration.max_lines = max_lines
        user_configuration.commit_interval = commit_interval
        user_configuration.updated_at = timezone.now()
        user_configuration.save()

    @classmethod
    def fetch_configurations(cls, user_id):
        """fetching configuration details related to the user"""
        from account.models.repository import Repository
        from account.models.source_configuration import SourceConfiguration
        from account.models.target_configuration import TargetConfiguration
        user_instance = UserAccount.objects.get(account_id=user_id)
        configuration_instance = UserConfiguration.objects.get(user=user_instance)
 
        repositories = Repository.objects.filter(user=user_instance)
        repository_details = []
        for repository in repositories:
            repo_id = repository.repo_id
            # fetching source configurations
            source_configurations = SourceConfiguration.objects.filter(
                repository=repository, user=user_instance
            )
            branch_details = []
            for source_configuration in source_configurations:
                source_branch = source_configuration.source_branch
                branch_name = source_branch.name
                commit_number = source_configuration.current_commit
                branch_details.append(
                    {"name": branch_name, "commit_number": commit_number}
                )
            # fetching target configurations
            try:
                target_configuration = TargetConfiguration.objects.get(
                    user=user_instance, repository=repository
                )
                target_branch = target_configuration.target_branch
                target = target_branch.name
            except TargetConfiguration.DoesNotExist:
                target = ""
            
            repository_details.append(
                {
                    "repo_id": repo_id,
                    "name": repository.name,
                    "url": repository.url,
                    "source_branches": branch_details,
                    "target_branch": target,
                }
            )
 
        return {
            "user_id": user_id,
            "commit_interval": configuration_instance.commit_interval,
            "max_lines": configuration_instance.max_lines,
            "repositories": repository_details,
        }