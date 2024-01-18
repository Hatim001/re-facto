from rest_framework import serializers

from account.models.account import UserAccount


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        exclude = ["access_token"]
