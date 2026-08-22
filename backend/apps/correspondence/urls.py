from rest_framework.routers import DefaultRouter

from .views import CorrespondenceViewSet


router = DefaultRouter()

router.register(
    r"correspondences",
    CorrespondenceViewSet,
    basename="correspondence",
)

urlpatterns = router.urls