from rest_framework.routers import DefaultRouter

from apps.payroll.views import (
    EmployeeSalaryViewSet,
    PayrollDeductionViewSet,
)


router = DefaultRouter()

router.register(
    r"salaries",
    EmployeeSalaryViewSet,
    basename="employee-salary",
)

router.register(
    r"deductions",
    PayrollDeductionViewSet,
    basename="payroll-deduction",
)

urlpatterns = router.urls