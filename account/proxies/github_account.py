import requests

from django.conf import settings
from django.middleware.csrf import rotate_token

from account.models.branch import Branch
from account.models.account import UserAccount
from account.models.repository import Repository
from core.utils.exceptions import ValidationError
from account.models.configuration import UserConfiguration
from account.models.source_configuration import SourceConfiguration
from account.models.target_configuration import TargetConfiguration
from account.serializers.serializer import UserAccountSerializer


class GitHubAccount(UserAccount):
    """
    A proxy class representing a GitHub account,
    inheriting from the UserAccount model/manager.
    """

    ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"

    class Meta:
        proxy = True

    @classmethod
    def fetch_access_token(cls, oauth_code):
        """
        Fetches and returns access token from GitHub.

        Args:
        - oauth_code: str, the OAuth code provided by GitHub.

        Returns:
        - str, the access token.
        """
        if not oauth_code:
            raise ValidationError("OAuth code not provided")

        token_payload = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_APP_SECRET,
            "code": oauth_code,
        }
        response = requests.post(
            url=cls.ACCESS_TOKEN_URL,
            headers={"Accept": "application/json", "scope": "repo"},
            data=token_payload,
        )
        return response.json().get("access_token")

    @classmethod
    def fetch_user_data(cls, access_token):
        """
        Fetches user data from the access token provided.

        Args:
        - access_token: str, the access token provided by GitHub.

        Returns:
        - dict, the user data.
        """
        user_url = "https://api.github.com/user"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.get(url=user_url, headers=headers)
        return response.json()

    @classmethod
    def prepare_configurations(cls, user_id):
        """
        Creates default configuration when new account is created.

        Args:
        - user_id: int, the ID of the user.
        """
        UserConfiguration.objects.create(
            user_id=user_id, commit_interval=5, max_lines=30
        )

    @classmethod
    def create_account(cls, user_data, access_token):
        """
        Creates account and configurations along with it.

        Args:
        - user_data: dict, the user data.
        - access_token: str, the access token provided by GitHub.
        """
        account_id = user_data.get("id")
        update_values = {
            "account_id": account_id,
            "access_token": access_token,
            "email": user_data.get("email"),
            "user_name": user_data.get("login"),
            "name": user_data.get("name"),
            "company": user_data.get("company"),
            "account_type": "GitHub",
        }
        if instance := UserAccount.objects.filter(account_id=account_id).first():
            instance.set_values(update_values)
            instance.save()
        else:
            instance = UserAccount.objects.create(**update_values)
            cls.prepare_configurations(instance.id)

    @classmethod
    def prepare_session(cls, request, user_data):
        """
        Prepares session for the current user login.

        Args:
        - request: HttpRequest, the HTTP request object.
        - user_data: dict, the user data.
        """
        user_id = user_data.get("id")
        user_instance = UserAccount.objects.get(account_id=user_id)
        rotate_token(request=request)

        request.session["isLoggedIn"] = True
        request.session["user_id"] = user_id
        request.session["user"] = UserAccountSerializer(user_instance).data
        request.session["avatar_url"] = user_data.get("avatar_url")
        request.session.save()
        request.session.set_expiry(settings.SESSION_EXPIRY)

    @classmethod
    def authorize(cls, oauth_code, request):
        """
        Authorizes and creates user.

        Args:
        - oauth_code: str, the OAuth code provided by GitHub.
        - request: HttpRequest, the HTTP request object.
        """
        access_token = cls.fetch_access_token(oauth_code=oauth_code)
        user_data = cls.fetch_user_data(access_token=access_token)
        cls.create_account(user_data=user_data, access_token=access_token)
        Repository.prepare_repositories(user=user_data, token=access_token)
        cls.prepare_session(request=request, user_data=user_data)
