import {
  createBrowserRouter,
  Navigate,
} from "react-router-dom"

import ProtectedRoute from "../components/common/ProtectedRoute"
import AppLayout from "../components/layout/AppLayout"

import LoginPage from "../pages/auth/LoginPage"
import DashboardPage from "../pages/dashboard/DashboardPage"
import EmployeesPage from "../pages/personnel/EmployeesPage"
import OrganizationPage from "../pages/organization/OrganizationPage"
import PayrollPage from "../pages/payroll/PayrollPage"

export const router =
  createBrowserRouter([
    {
      path: "/login",
      element: <LoginPage />,
    },

    {
      element: <ProtectedRoute />,

      children: [
        {
          element: <AppLayout />,

          children: [
            {
              path: "/dashboard",
              element: <DashboardPage />,
            },

            {
              path: "/employees",
              element: <EmployeesPage />,
            },
            {
              path: "/organization",
              element: <OrganizationPage />,
            },
            {
              path: "/payroll",
              element: <PayrollPage />,
            },
            
          ],
        },
      ],
    },

    {
      path: "*",

      element: (
        <Navigate
          to="/dashboard"
          replace
        />
      ),
    },
  ])