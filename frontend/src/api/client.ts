/**
 * Base API client for making HTTP requests to the backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * Error class for API errors.
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/**
 * Make a GET request.
 */
export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError(
      errorData.message || 'Request failed',
      response.status,
      errorData
    )
  }

  return response.json()
}

/**
 * Make a POST request.
 */
export async function apiPost<T, D = unknown>(path: string, data: D): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError(
      errorData.message || 'Request failed',
      response.status,
      errorData
    )
  }

  return response.json()
}

/**
 * Make a PUT request.
 */
export async function apiPut<T, D = unknown>(path: string, data: D): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError(
      errorData.message || 'Request failed',
      response.status,
      errorData
    )
  }

  return response.json()
}

/**
 * Make a DELETE request.
 */
export async function apiDelete<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError(
      errorData.message || 'Request failed',
      response.status,
      errorData
    )
  }

  // DELETE may return empty body
  const text = await response.text()
  return text ? JSON.parse(text) : ({} as T)
}
