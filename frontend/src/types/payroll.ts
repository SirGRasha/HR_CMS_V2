export interface EmployeeSalary {
  id: number
  employee: number

  year: number
  month: number

  monthly_wage: string
  worker_food_allowance: string
  housing_allowance: string
  marriage_allowance: string

  notes: string

  eligible_children_count: number
  daily_wage: string
  child_allowance_per_child: string
  calculated_child_allowance: string
  total_eligible_benefits: string

  created_at: string
  updated_at: string
}

export interface EmployeeSalaryFilters {
  employee?: number
  year?: number
  month?: number
}

export interface PayrollDeduction {
  id: number
  salary: number

  deduction_type:
    | "insurance"
    | "tax"
    | "advance"
    | "loan"
    | "absence"
    | "other"

  deduction_type_display: string

  amount: string
  description: string

  created_at: string
  updated_at: string
}

export interface PayrollDeductionFilters {
  salary?: number
  deduction_type?:
    | "insurance"
    | "tax"
    | "advance"
    | "loan"
    | "absence"
    | "other"
}

export interface PayrollEarnings {
  monthly_wage: string
  worker_food_allowance: string
  housing_allowance: string
  marriage_allowance: string
  child_allowance: string
  gross_earnings: string
}

export interface PayrollChildren {
  eligible_count: number
  allowance_per_child: string
}

export interface PayrollDeductions {
  insurance: string
  tax: string
  advance: string
  loan: string
  absence: string
  other: string
  total_deductions: string
}

export interface PayrollCalculation {
  salary_id: number
  employee: number

  period: {
    year: number
    month: number
  }

  earnings: PayrollEarnings
  children: PayrollChildren
  deductions: PayrollDeductions

  net_salary: string
}