from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from account.models import UserAccount
from account.models.account import GITHUB, GITLAB


class UserAccountTestCase(TestCase):
    def setUp(self):
        self.user_account = UserAccount.objects.create(
            account_id="123456",
            access_token="abcdef",
            email="test@example.com",
            account_type=GITHUB,
            user_name="testuser",
            name="Test User",
            company="Test Company",
        )

    def test_user_account_creation(self):
        self.assertEqual(self.user_account.account_id, "123456")
        self.assertEqual(self.user_account.access_token, "abcdef")
        self.assertEqual(self.user_account.email, "test@example.com")
        self.assertEqual(self.user_account.account_type, GITHUB)
        self.assertEqual(self.user_account.user_name, "testuser")
        self.assertEqual(self.user_account.name, "Test User")
        self.assertEqual(self.user_account.company, "Test Company")

    def test_user_account_retrieval(self):
        retrieved_account = UserAccount.objects.get(account_id="123456")
        self.assertEqual(retrieved_account, self.user_account)

    def test_user_account_update(self):
        self.user_account.email = "new_email@example.com"
        self.user_account.save()
        updated_account = UserAccount.objects.get(account_id="123456")
        self.assertEqual(updated_account.email, "new_email@example.com")

    def test_user_account_timestamps(self):
        self.assertIsNotNone(self.user_account.created_at)
        self.assertIsNotNone(self.user_account.updated_at)
        original_updated_at = self.user_account.updated_at
        delay = timedelta(seconds=1)
        new_timestamp = timezone.now() + delay
        UserAccount.objects.filter(account_id="123456").update(updated_at=new_timestamp)
        updated_account = UserAccount.objects.get(account_id="123456")
        self.assertGreater(updated_account.updated_at, original_updated_at)
