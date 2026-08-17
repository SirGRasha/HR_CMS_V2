from rest_framework.routers import DefaultRouter

from apps.organization.views import (
    OrganizationUnitViewSet,
    PositionViewSet,
)


router = DefaultRouter()

router.register(
    r"units",
    OrganizationUnitViewSet,
    basename="organization-unit",
)

router.register(
    r"positions",
    PositionViewSet,
    basename="position",
)


urlpatterns = router.urls
