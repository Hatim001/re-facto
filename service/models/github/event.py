from typing import Optional

from django.conf import settings
from django.http import HttpRequest
import requests

from account.proxies.github_account import GitHubAccount
from core.utils.requests import fetch
from core.utils.exceptions import ValidationError
from service.models.base.event import BaseEvent


class GithubEvent(BaseEvent):
    """Manages GitHub's events"""

    ACCEPTED_EVENTS = ["push", "ping", "installation", "github_app_authorization"]

    def __init__(self, request: HttpRequest) -> None:
        super().__init__(request)
        self.type: Optional[str] = self.headers.get("X-GitHub-Event")
        self.account: Optional[GitHubAccount] = None

    def validate_event(self) -> None:
        """Validates if event is of push type"""
        if self.type not in self.ACCEPTED_EVENTS:
            raise ValidationError("Event type not supported!!")

    def validate_token(self) -> None:
        """Checks if the access token is expired or not"""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"access_token": self.account.access_token}
        status, _ = fetch(
            url=f"https://api.github.com/applications/{settings.GITHUB_CLIENT_ID}/token",
            method="POST",
            headers=headers,
            payload=data,
            auth=(settings.GITHUB_CLIENT_ID, settings.GITHUB_APP_SECRET),
        )
        if status != 200:
            raise ValidationError("Access token expired!!")

    def validate_account(self) -> None:
        """Checks whether the account and repository is associated with our app"""
        account_id = self.payload.get("sender", {}).get("id")
        self.account = GitHubAccount.objects.filter(account_id=account_id).first()
        if not self.account:
            raise ValidationError("Account does not exist!!")

        self.validate_token()

    def listen(self):
        """Listener for GitHub's events"""
        self.validate_event()
        self.validate_account()
        return self
