export type OrganizationUnitType =
  | "company"
  | "management"
  | "deputy"
  | "department"
  | "unit"
  | "section"

export interface OrganizationUnit {
  id: number
  code: string
  name: string
  unit_type: OrganizationUnitType
  parent: number | null
  is_active: boolean
  description: string
  created_at: string
  updated_at: string
}

export interface Position {
  id: number
  code: string
  title: string
  organization_unit: number
  is_active: boolean
  description: string
  created_at: string
  updated_at: string
}

export interface OrganizationUnitFilters {
  is_active?: boolean
  unit_type?: OrganizationUnitType
  parent?: number | null
}

export interface PositionFilters {
  is_active?: boolean
  organization_unit?: number
}