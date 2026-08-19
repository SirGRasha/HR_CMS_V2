from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "username",
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        request = self.context.get("request")

        if request and not request.user.is_superuser:
            if attrs.get("is_staff", False):
                raise serializers.ValidationError(
                    {
                        "is_staff": (
                            "Only superusers can create "
                            "staff users."
                        )
                    }
                )

            if attrs.get("is_superuser", False):
                raise serializers.ValidationError(
                    {
                        "is_superuser": (
                            "Only superusers can create "
                            "superusers."
                        )
                    }
                )

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = [
            "username",
        ]

    def validate(self, attrs):
        request = self.context.get("request")

        if not request:
            return attrs

        # Only superusers can change privileged flags.
        if not request.user.is_superuser:
            if "is_staff" in attrs:
                raise serializers.ValidationError(
                    {
                        "is_staff": (
                            "Only superusers can change "
                            "staff status."
                        )
                    }
                )

            if "is_superuser" in attrs:
                raise serializers.ValidationError(
                    {
                        "is_superuser": (
                            "Only superusers can change "
                            "superuser status."
                        )
                    }
                )

        # A superuser must not be able to disable or demote
        # their own account.
        if self.instance and request.user == self.instance:
            if (
                "is_superuser" in attrs
                and attrs["is_superuser"] is False
            ):
                raise serializers.ValidationError(
                    {
                        "is_superuser": (
                            "A superuser cannot remove "
                            "their own superuser status."
                        )
                    }
                )

            if (
                "is_staff" in attrs
                and attrs["is_staff"] is False
            ):
                raise serializers.ValidationError(
                    {
                        "is_staff": (
                            "A superuser cannot remove "
                            "their own staff status."
                        )
                    }
                )

            if (
                "is_active" in attrs
                and attrs["is_active"] is False
            ):
                raise serializers.ValidationError(
                    {
                        "is_active": (
                            "A superuser cannot deactivate "
                            "their own account."
                        )
                    }
                )

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        required=True,
    )

    def validate_new_password(self, value):
        validate_password(value)
        return value

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        write_only=True,
        required=True,
    )

    def validate(self, attrs):
        refresh_token = attrs["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            raise serializers.ValidationError(
                {
                    "refresh": (
                        "Invalid or already blacklisted "
                        "refresh token."
                    )
                }
            )

        return attrs