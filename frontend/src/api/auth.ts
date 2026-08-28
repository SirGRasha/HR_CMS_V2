import { apiRequest } from "./client"
import type {
  LoginCredentials,
  TokenResponse,
  User,
} from "../types/auth"

export async function login(
  credentials: LoginCredentials,
): Promise<TokenResponse> {
  const response = await fetch(
    "http://127.0.0.1:8000/api/accounts/token/",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    },
  )

  if (!response.ok) {
    let errorData: unknown = null

    try {
      errorData = await response.json()
    } catch {
      // Ignore invalid JSON response.
    }

    throw {
      status: response.status,
      data: errorData,
    }
  }

  const data =
    (await response.json()) as TokenResponse

  localStorage.setItem(
    "access_token",
    data.access,
  )

  localStorage.setItem(
    "refresh_token",
    data.refresh,
  )

  return data
}

export async function getMe(): Promise<User> {
  return apiRequest<User>(
    "/accounts/me/",
  )
}

export async function refreshAccessToken(): Promise<TokenResponse> {
  const refreshToken =
    localStorage.getItem("refresh_token")

  if (!refreshToken) {
    throw new Error(
      "Refresh token not found.",
    )
  }

  const response = await fetch(
    "http://127.0.0.1:8000/api/accounts/token/refresh/",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        refresh: refreshToken,
      }),
    },
  )

  if (!response.ok) {
    clearTokens()

    throw new Error(
      "Unable to refresh access token.",
    )
  }

  const data =
    (await response.json()) as TokenResponse

  localStorage.setItem(
    "access_token",
    data.access,
  )

  if (data.refresh) {
    localStorage.setItem(
      "refresh_token",
      data.refresh,
    )
  }

  return data
}

export async function logout(): Promise<void> {
  const refreshToken =
    localStorage.getItem("refresh_token")

  if (!refreshToken) {
    clearTokens()
    return
  }

  try {
    await apiRequest(
      "/accounts/logout/",
      {
        method: "POST",
        body: JSON.stringify({
          refresh: refreshToken,
        }),
      },
    )
  } finally {
    clearTokens()
  }
}

export function clearTokens(): void {
  localStorage.removeItem(
    "access_token",
  )

  localStorage.removeItem(
    "refresh_token",
  )
}

export function isAuthenticated(): boolean {
  return Boolean(
    localStorage.getItem("access_token"),
  )
}