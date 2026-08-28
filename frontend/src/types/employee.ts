export interface OrganizationUnit {
  id: number
  code: string
  name: string
}

export interface PositionDetail {
  id: number
  code: string
  title: string
  is_active: boolean
  organization_unit: OrganizationUnit
}

export interface Employee {
  id: number
  user: number | null

  personnel_code: string

  first_name: string
  last_name: string

  gender: string
  employee_group: string

  department: string
  job_title: string

  position: number | null
  position_detail: PositionDetail | null

  start_date: string | null
  insurance_date: string | null
  insurance_number: string | null
  birth_date: string | null

  national_id: string
  birth_certificate_number: string | null
  father_name: string

  education_level: string
  field_of_study: string | null
  student_number: string | null

  military_status: string
  marital_status: string

  child_count: number

  landline_phone: string | null
  residence_area: string | null
  address: string | null

  transportation_status: string
  transportation_description: string | null

  contract_title: string | null
  contract_position: string | null

  notes: string | null

  is_active: boolean

  created_at: string
  updated_at: string
}

export interface EmployeeListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Employee[]
}

export interface EmployeeFilters {
  position?: number
  organization_unit?: number
  is_active?: boolean
  employee_group?: string
}