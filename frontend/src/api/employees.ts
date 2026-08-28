import { apiRequest } from "./client"
import type {
  Employee,
  EmployeeFilters,
  EmployeeListResponse,
} from "../types/employee"

function buildQueryString(
  filters: EmployeeFilters = {},
): string {
  const params = new URLSearchParams()

  if (filters.position !== undefined) {
    params.set(
      "position",
      String(filters.position),
    )
  }

  if (
    filters.organization_unit !==
    undefined
  ) {
    params.set(
      "organization_unit",
      String(
        filters.organization_unit,
      ),
    )
  }

  if (filters.is_active !== undefined) {
    params.set(
      "is_active",
      String(filters.is_active),
    )
  }

  if (
    filters.employee_group
  ) {
    params.set(
      "employee_group",
      filters.employee_group,
    )
  }

  const query = params.toString()

  return query
    ? `?${query}`
    : ""
}

export async function getEmployees(
  filters: EmployeeFilters = {},
): Promise<EmployeeListResponse> {
  return apiRequest<EmployeeListResponse>(
    `/personnel/employees/${buildQueryString(
      filters,
    )}`,
  )
}

export async function getEmployee(
  id: number,
): Promise<Employee> {
  return apiRequest<Employee>(
    `/personnel/employees/${id}/`,
  )
}

export async function createEmployee(
  data: Partial<Employee>,
): Promise<Employee> {
  return apiRequest<Employee>(
    "/personnel/employees/",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  )
}

export async function updateEmployee(
  id: number,
  data: Partial<Employee>,
): Promise<Employee> {
  return apiRequest<Employee>(
    `/personnel/employees/${id}/`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    },
  )
}

export async function patchEmployee(
  id: number,
  data: Partial<Employee>,
): Promise<Employee> {
  return apiRequest<Employee>(
    `/personnel/employees/${id}/`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    },
  )
}

export async function deleteEmployee(
  id: number,
): Promise<void> {
  return apiRequest<void>(
    `/personnel/employees/${id}/`,
    {
      method: "DELETE",
    },
  )
}