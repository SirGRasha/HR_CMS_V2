const API_BASE_URL = "http://127.0.0.1:8000/api"

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const accessToken = localStorage.getItem("access_token")

  const headers = new Headers(options.headers)

  headers.set("Content-Type", "application/json")

  if (accessToken) {
    headers.set(
      "Authorization",
      `Bearer ${accessToken}`,
    )
  }

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...options,
      headers,
    },
  )

  if (!response.ok) {
    let errorData: unknown = null

    try {
      errorData = await response.json()
    } catch {
      // Response may not contain JSON.
    }

    throw {
      status: response.status,
      data: errorData,
    }
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}