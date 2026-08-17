from rest_framework.routers import DefaultRouter

from .views import (
    EmployeeBankAccountViewSet,
    EmployeeChildViewSet,
    EmployeeDocumentViewSet,
    EmployeePhoneViewSet,
    EmployeePromissoryNoteViewSet,
    EmployeeViewSet,
)


router = DefaultRouter()

router.register(
    r"employees",
    EmployeeViewSet,
    basename="employee",
)

router.register(
    r"children",
    EmployeeChildViewSet,
    basename="employee-child",
)

router.register(
    r"phones",
    EmployeePhoneViewSet,
    basename="employee-phone",
)

router.register(
    r"documents",
    EmployeeDocumentViewSet,
    basename="employee-document",
)

router.register(
    r"promissory-notes",
    EmployeePromissoryNoteViewSet,
    basename="employee-promissory-note",
)

router.register(
    r"bank-accounts",
    EmployeeBankAccountViewSet,
    basename="employee-bank-account",
)

urlpatterns = router.urls