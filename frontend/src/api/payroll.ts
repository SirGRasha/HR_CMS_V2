import { apiRequest } from "./client"

import type {
  EmployeeSalary,
  EmployeeSalaryFilters,
  PayrollCalculation,
  PayrollDeduction,
  PayrollDeductionFilters,
} from "../types/payroll"

/* =========================
   Salary Query
   ========================= */

function buildSalaryQueryString(
  filters: EmployeeSalaryFilters = {},
): string {
  const params = new URLSearchParams()

  if (filters.employee !== undefined) {
    params.set(
      "employee",
      String(filters.employee),
    )
  }

  if (filters.year !== undefined) {
    params.set(
      "year",
      String(filters.year),
    )
  }

  if (filters.month !== undefined) {
    params.set(
      "month",
      String(filters.month),
    )
  }

  const query = params.toString()

  return query ? `?${query}` : ""
}

/* =========================
   Salary API
   ========================= */

export async function getSalaries(
  filters: EmployeeSalaryFilters = {},
): Promise<EmployeeSalary[]> {
  return apiRequest<EmployeeSalary[]>(
    `/payroll/salaries/${buildSalaryQueryString(
      filters,
    )}`,
  )
}

export async function getSalary(
  id: number,
): Promise<EmployeeSalary> {
  return apiRequest<EmployeeSalary>(
    `/payroll/salaries/${id}/`,
  )
}

export async function createSalary(
  data: Partial<EmployeeSalary>,
): Promise<EmployeeSalary> {
  return apiRequest<EmployeeSalary>(
    "/payroll/salaries/",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  )
}

export async function updateSalary(
  id: number,
  data: Partial<EmployeeSalary>,
): Promise<EmployeeSalary> {
  return apiRequest<EmployeeSalary>(
    `/payroll/salaries/${id}/`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    },
  )
}

export async function patchSalary(
  id: number,
  data: Partial<EmployeeSalary>,
): Promise<EmployeeSalary> {
  return apiRequest<EmployeeSalary>(
    `/payroll/salaries/${id}/`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    },
  )
}

export async function deleteSalary(
  id: number,
): Promise<void> {
  return apiRequest<void>(
    `/payroll/salaries/${id}/`,
    {
      method: "DELETE",
    },
  )
}

export async function calculateSalary(
  id: number,
): Promise<PayrollCalculation> {
  return apiRequest<PayrollCalculation>(
    `/payroll/salaries/${id}/calculate/`,
  )
}

/* =========================
   Deduction Query
   ========================= */

function buildDeductionQueryString(
  filters: PayrollDeductionFilters = {},
): string {
  const params = new URLSearchParams()

  if (filters.salary !== undefined) {
    params.set(
      "salary",
      String(filters.salary),
    )
  }

  if (filters.deduction_type) {
    params.set(
      "deduction_type",
      filters.deduction_type,
    )
  }

  const query = params.toString()

  return query ? `?${query}` : ""
}

/* =========================
   Deduction API
   ========================= */

export async function getDeductions(
  filters: PayrollDeductionFilters = {},
): Promise<PayrollDeduction[]> {
  return apiRequest<PayrollDeduction[]>(
    `/payroll/deductions/${buildDeductionQueryString(
      filters,
    )}`,
  )
}

export async function getDeduction(
  id: number,
): Promise<PayrollDeduction> {
  return apiRequest<PayrollDeduction>(
    `/payroll/deductions/${id}/`,
  )
}

export async function createDeduction(
  data: Partial<PayrollDeduction>,
): Promise<PayrollDeduction> {
  return apiRequest<PayrollDeduction>(
    "/payroll/deductions/",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  )
}

export async function updateDeduction(
  id: number,
  data: Partial<PayrollDeduction>,
): Promise<PayrollDeduction> {
  return apiRequest<PayrollDeduction>(
    `/payroll/deductions/${id}/`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    },
  )
}

export async function patchDeduction(
  id: number,
  data: Partial<PayrollDeduction>,
): Promise<PayrollDeduction> {
  return apiRequest<PayrollDeduction>(
    `/payroll/deductions/${id}/`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    },
  )
}

export async function deleteDeduction(
  id: number,
): Promise<void> {
  return apiRequest<void>(
    `/payroll/deductions/${id}/`,
    {
      method: "DELETE",
    },
  )
}