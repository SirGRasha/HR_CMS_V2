import { apiRequest } from "./client"

import type {
  OrganizationUnit,
  OrganizationUnitFilters,
  Position,
  PositionFilters,
} from "../types/organization"

function buildOrganizationUnitQueryString(
  filters: OrganizationUnitFilters = {},
): string {
  const params = new URLSearchParams()

  if (filters.is_active !== undefined) {
    params.set(
      "is_active",
      String(filters.is_active),
    )
  }

  if (filters.unit_type) {
    params.set(
      "unit_type",
      filters.unit_type,
    )
  }

  if (filters.parent !== undefined) {
    params.set(
      "parent",
      filters.parent === null
        ? "null"
        : String(filters.parent),
    )
  }

  const query = params.toString()

  return query ? `?${query}` : ""
}

function buildPositionQueryString(
  filters: PositionFilters = {},
): string {
  const params = new URLSearchParams()

  if (filters.is_active !== undefined) {
    params.set(
      "is_active",
      String(filters.is_active),
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

  const query = params.toString()

  return query ? `?${query}` : ""
}

/* =========================
   Organization Units
   ========================= */

export async function getOrganizationUnits(
  filters: OrganizationUnitFilters = {},
): Promise<OrganizationUnit[]> {
  return apiRequest<OrganizationUnit[]>(
    `/organization/units/${buildOrganizationUnitQueryString(
      filters,
    )}`,
  )
}

export async function getOrganizationUnit(
  id: number,
): Promise<OrganizationUnit> {
  return apiRequest<OrganizationUnit>(
    `/organization/units/${id}/`,
  )
}

export async function createOrganizationUnit(
  data: Partial<OrganizationUnit>,
): Promise<OrganizationUnit> {
  return apiRequest<OrganizationUnit>(
    "/organization/units/",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  )
}

export async function updateOrganizationUnit(
  id: number,
  data: Partial<OrganizationUnit>,
): Promise<OrganizationUnit> {
  return apiRequest<OrganizationUnit>(
    `/organization/units/${id}/`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    },
  )
}

export async function patchOrganizationUnit(
  id: number,
  data: Partial<OrganizationUnit>,
): Promise<OrganizationUnit> {
  return apiRequest<OrganizationUnit>(
    `/organization/units/${id}/`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    },
  )
}

export async function deleteOrganizationUnit(
  id: number,
): Promise<void> {
  return apiRequest<void>(
    `/organization/units/${id}/`,
    {
      method: "DELETE",
    },
  )
}

/* =========================
   Positions
   ========================= */

export async function getPositions(
  filters: PositionFilters = {},
): Promise<Position[]> {
  return apiRequest<Position[]>(
    `/organization/positions/${buildPositionQueryString(
      filters,
    )}`,
  )
}

export async function getPosition(
  id: number,
): Promise<Position> {
  return apiRequest<Position>(
    `/organization/positions/${id}/`,
  )
}

export async function createPosition(
  data: Partial<Position>,
): Promise<Position> {
  return apiRequest<Position>(
    "/organization/positions/",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  )
}

export async function updatePosition(
  id: number,
  data: Partial<Position>,
): Promise<Position> {
  return apiRequest<Position>(
    `/organization/positions/${id}/`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    },
  )
}

export async function patchPosition(
  id: number,
  data: Partial<Position>,
): Promise<Position> {
  return apiRequest<Position>(
    `/organization/positions/${id}/`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    },
  )
}

export async function deletePosition(
  id: number,
): Promise<void> {
  return apiRequest<void>(
    `/organization/positions/${id}/`,
    {
      method: "DELETE",
    },
  )
}