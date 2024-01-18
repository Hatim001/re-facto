from django.db import models

from core.models.base import BaseModel

GITHUB = "GITHUB"
GITLAB = "GITLAB"
ACCOUNT_TYPES = ((GITHUB, GITHUB), (GITLAB, GITLAB))


class UserAccount(BaseModel):
    """Model/Manager for service accounts"""

    account_id = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True)
    account_type = models.CharField(
        choices=ACCOUNT_TYPES, max_length=255, default=GITHUB
    )
    user_name = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True)
    company = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "UserAccount"
