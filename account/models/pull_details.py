from django.db import models

from account.models import UserAccount
from core.models.base import BaseModel


class PullDetails(BaseModel):

    """Model/Manager for Pull details"""

    pull_id = models.IntegerField()
    Repo_name = models.CharField(max_length=255)
    author = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, to_field="user_name"
    )
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "PullDetails"

    @classmethod
    def save_pull_details(cls, data_dict):
        try:
            author_user_name = data_dict.get("author")
            author = UserAccount.objects.get(user_name=author_user_name)

        except UserAccount.DoesNotExist:
            raise ValueError(
                f"UserAccount with user_name {author_user_name} does not exist."
            )

        instance = cls(
            pull_id=data_dict.get("pull_id"),
            Repo_name=data_dict.get("Repo_name"),
            author=author,
            title=data_dict.get("title"),
        )
        instance.save()

        return instance
