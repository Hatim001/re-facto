from django.test import TestCase

from account.models import PullDetails, UserAccount
from account.models.account import GITHUB, GITLAB


class PullDetailsTestCase(TestCase):
    def setUp(self):
        self.sample_pull_request = "Sample Pull Request"
        self.user_account = UserAccount.objects.create(
            account_id="123456",
            access_token="abcdef",
            email="test@example.com",
            account_type=GITHUB,
            user_name="testuser",
            name="Test User",
            company="Test Company",
        )
        self.pull_details_data = {
            "pull_id": 1,
            "Repo_name": "sample_repo",
            "author": "testuser",
            "title": self.sample_pull_request,
        }

    def test_create_pull_details_instance(self):
        author_user_name = self.pull_details_data["author"]
        author_user_account = UserAccount.objects.get(user_name=author_user_name)
        pull_details_instance = PullDetails(
            pull_id=self.pull_details_data["pull_id"],
            Repo_name=self.pull_details_data["Repo_name"],
            author=author_user_account,
            title=self.pull_details_data["title"],
        )
        pull_details_instance.save()
        retrieved_pull_details = PullDetails.objects.get(pull_id=1)
        self.assertEqual(retrieved_pull_details.Repo_name, "sample_repo")
        self.assertEqual(retrieved_pull_details.author, author_user_account)
        self.assertEqual(retrieved_pull_details.title, self.sample_pull_request)

    def test_save_pull_details_class_method(self):
        PullDetails.save_pull_details(self.pull_details_data)
        retrieved_pull_details = PullDetails.objects.get(pull_id=1)
        self.assertEqual(retrieved_pull_details.Repo_name, "sample_repo")
        author_user_name = self.pull_details_data["author"]
        author_user_account = UserAccount.objects.get(user_name=author_user_name)
        self.assertEqual(retrieved_pull_details.author, author_user_account)
        self.assertEqual(retrieved_pull_details.title, self.sample_pull_request)
