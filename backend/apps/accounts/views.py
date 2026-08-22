from rest_framework import status, viewsets
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import User
from apps.accounts.permissions import (
    CanChangeUserPassword,
    IsStaffOrReadOnly,
    IsSuperuser,
)
from apps.accounts.serializers import (
    ChangePasswordSerializer,
    LogoutSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from apps.accounts.jwt_serializers import (
    AuditTokenObtainPairSerializer,
)
from apps.audit.services import AuditService
from apps.audit.utils import build_changes

class AuditTokenObtainPairView(
    TokenObtainPairView
):
    permission_classes = [AllowAny]
    serializer_class = AuditTokenObtainPairSerializer

#(class LogoutAPIView(APIView):
#    permission_classes = [IsAuthenticated]
#
 #   def post(self, request):
  #      serializer = TokenBlacklistSerializer(
   #         data=request.data
    #    )
#
 #       serializer.is_valid(
  #          raise_exception=True
   #     )
#
 #       serializer.save()
#
 #       AuditService.logout(
  #          actor=request.user,
   #         instance=request.user,
    #        request=request,
     #   )
#
 #       return Response(
  #          {
   ###       status=status.HTTP_200_OK,
      #  )

class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")

    AUDIT_UPDATE_FIELDS = [
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
    ]

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [
                IsAuthenticated,
                IsSuperuser,
            ]
        else:
            permission_classes = [
                IsAuthenticated,
                IsStaffOrReadOnly,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer

        if self.action in [
            "update",
            "partial_update",
        ]:
            return UserUpdateSerializer

        return UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()

        AuditService.create(
            actor=self.request.user,
            instance=user,
            request=self.request,
        )

    def perform_update(self, serializer):
        old_user = User.objects.get(
            pk=serializer.instance.pk
        )

        user = serializer.save()

        changes = build_changes(
            old_user,
            user,
            self.AUDIT_UPDATE_FIELDS,
        )

        if changes:
            AuditService.update(
                actor=self.request.user,
                instance=user,
                request=self.request,
                changes=changes,
            )

    def perform_destroy(self, instance):
        AuditService.delete(
            actor=self.request.user,
            instance=instance,
            request=self.request,
        )

        instance.delete()


class UserPasswordAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        CanChangeUserPassword,
    ]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        permission = CanChangeUserPassword()

        if not permission.has_object_permission(
            request,
            self,
            user,
        ):
            return Response(
                {"detail": "You do not have permission."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ChangePasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user.set_password(
            serializer.validated_data["new_password"]
        )
        user.save(update_fields=["password"])

        AuditService.password_change(
            actor=request.user,
            instance=user,
            request=request,
        )

        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        AuditService.logout(
            actor=request.user,
            instance=request.user,
            request=request,
        )

        return Response(
            {
                "detail": "Logout successful."
            },
            status=status.HTTP_200_OK,
        )