from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)

from apps.audit.services import AuditService


class AuditTokenObtainPairSerializer(
    TokenObtainPairSerializer
):
    def validate(self, attrs):
        data = super().validate(attrs)

        AuditService.login(
            actor=self.user,
            instance=self.user,
            request=self.context.get("request"),
        )

        return data