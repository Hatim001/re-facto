from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer

from account.models.account import UserAccount
from account.models.branch import Branch
from account.models.configuration import UserConfiguration
from account.models.repository import Repository
from account.models.source_configuration import SourceConfiguration
from account.models.target_configuration import TargetConfiguration
from account.proxies.github_account import GitHubAccount
from core.utils.base_view import BaseView
from core.utils.exceptions import ValidationError


class GitHubConfigurationView(BaseView):
    model = GitHubAccount

    def get(self, request, *args, **kwargs):
        """fetching user configurations"""
        user_id = request.session.get("user_id")

        user_instance = self.get_user_instance(user_id)
        user_configuration = UserConfiguration.objects.get(user=user_instance)

        repositories_data = self.fetch_repositories_data(user_id)
        for each_repository in repositories_data:
            self.configure_repository_instance(
                user_instance, each_repository
            )
            self.configure_source_branches(
                user_id,
                each_repository.get("repo_id"),
                each_repository.get("source_branches"),
            )
            self.configure_target_branches(
                user_id,
                each_repository.get("repo_id"),
                each_repository.get("target_branches"),
            )

        return JsonResponse(
            {
                "repositories": repositories_data,
                "commit_interval": user_configuration.commit_interval,
                "max_lines": user_configuration.max_lines,
            }
        )

    def post(self, request, *args, **kwargs):
        """adding user configurations"""
        user_id = request.session.get("user_id")
        configs = request.data
        commit_interval = configs.get("commit_interval")
        max_lines = configs.get("max_lines")
        self.validate_configuration(
            max_lines=max_lines, commit_interval=commit_interval
        )
        UserConfiguration.update_configuration(
            commit_interval=commit_interval, max_lines=max_lines, user_id=user_id
        )

        for repo in configs.get("repositories"):
            names = []
            names.extend(self.process_source_branches(user_id, repo))
            names.extend(self.process_target_branches(user_id, repo))
            self.cleanup_branches(
                user_id=user_id, names=names, repo_id=repo.get("repo_id")
            )

        return HttpResponse("Successfully Updated")

    def get_user_instance(self, user_id):
        """returns user instance corresponding to user id"""
        return UserAccount.objects.get(account_id=user_id)

    def fetch_repositories_data(self, user_id):
        """fetches all the repository details
        including source and target branches"""
        return Repository.read_repositories(user_id=user_id)

    def configure_repository_instance(self, user_instance, repository):
        """create or get repository with
        given user instance and repo details"""
        return Repository.objects.get_or_create(
            user=user_instance,
            repo_id=repository.get("repo_id"),
            name=repository.get("name"),
            url=repository.get("url"),
        )

    def configure_source_branches(self, user_id, repo_id, source_branches):
        """modify source_branches data
        according to present configuration
        is_select is set to true if source_branch is configured"""
        configured_source_branches = SourceConfiguration.fetch_configured_branches(
            user_id=user_id, repo_id=repo_id
        )
        for source_branch in source_branches:
            if source_branch.get("name") in configured_source_branches:
                source_branch["is_selected"] = True

    def configure_target_branches(self, user_id, repo_id, target_branches):
        """modify target_branches data
        according to present configuration
        is_select is set to true if target_branch is configured"""
        configured_target_branch = TargetConfiguration.fetch_configuration(
            user_id=user_id, repo_id=repo_id
        )
        if configured_target_branch is not None:
            for target_branch in target_branches:
                if target_branch.get("name") == configured_target_branch.name:
                    target_branch["is_selected"] = True

    def update_source_configuration(self, user_id, repo_id, branch_name):
        """adding new source configuration"""
        SourceConfiguration.configure_branch(
            user_id=user_id, repo_id=repo_id, branch_name=branch_name
        )

    def update_target_configuration(self, user_id, repo_id, target_branch):
        """adding new target configuration"""
        TargetConfiguration.add_configuration(
            user_id=user_id, repo_id=repo_id, target_branch=target_branch
        )

    def cleanup_branches(self, user_id, repo_id, names):
        """branch cleanup once configurations are set
        remove unwanted branches"""
        Branch.cleanup(user_id=user_id, names=names, repo_id=repo_id)

    def process_source_branches(self, user_id, repo):
        """process the source branches configuration and cleanup"""
        names = []
        for branch in repo.get("source_branches", []):
            if branch.get("is_selected", False):
                names.append(branch.get("name"))
                self.update_source_configuration(
                    user_id=user_id,
                    repo_id=repo.get("repo_id"),
                    branch_name=branch.get("name"),
                )
        return names

    def process_target_branches(self, user_id, repo):
        """process the target branches configuration and cleanup"""
        names = []
        added = False
        for target_branch in repo.get("target_branches", []):
            if target_branch.get("is_selected", False):
                if added:
                    raise ValidationError("Cannot select more than one target branch")
                names.append(target_branch.get("name"))
                self.update_target_configuration(
                    user_id=user_id,
                    repo_id=repo.get("repo_id"),
                    target_branch=target_branch.get("name"),
                )
                added = True
        return names

    @classmethod
    def validate_configuration(cls, max_lines, commit_interval):
        """validating configurations"""
        if max_lines <= 0:
            raise ValidationError(
                "The maximum number of lines cannot be less than zero."
            )
        if commit_interval <= 0:
            raise ValidationError("The commit interval cannot be less than zero")
