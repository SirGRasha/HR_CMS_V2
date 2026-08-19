from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from apps.accounts.views import (
    AuditTokenObtainPairView,
    MeAPIView,
    UserPasswordAPIView,
    UserViewSet,
)


router = DefaultRouter()

router.register(
    "users",
    UserViewSet,
    basename="user",
)


urlpatterns = [
    path(
    "token/",
    AuditTokenObtainPairView.as_view(),
    name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "me/",
        MeAPIView.as_view(),
        name="me",
    ),
    path(
        "",
        include(router.urls),
    ),
    path(
        "users/<int:pk>/password/",
        UserPasswordAPIView.as_view(),
        name="user_password",
    ),
]