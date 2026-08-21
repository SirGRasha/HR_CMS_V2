from rest_framework.routers import DefaultRouter

from .views import HRRequestViewSet


router = DefaultRouter()

router.register(
    r"requests",
    HRRequestViewSet,
    basename="hr-request",
)

urlpatterns = router.urls