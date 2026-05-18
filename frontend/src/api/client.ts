/**
 * The API client: one thin function per backend endpoint.
 *
 * Every call goes through `request()`, which prefixes `/api`, parses the
 * JSON body, and turns any non-2xx response into a thrown Error — so the
 * page components only ever deal with resolved data or a caught error.
 */

import type {
  DriverProgression,
  DriverStats,
  Leaderboard,
  SessionDetail,
  SessionSummary,
  SessionUploadResponse,
} from './types'

// Requests target a relative `/api/...` path. In development, Vite's proxy
// (see vite.config.ts) forwards that to the FastAPI server on port 8000.
const API_BASE = '/api'

/**
 * Make a request and return the parsed JSON body, typed as `T`.
 * `<T>` is a generic — each caller below states the shape it expects back.
 */
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options)

  if (!response.ok) {
    // FastAPI reports errors as `{ "detail": "..." }`.
    const body = await response.json().catch(() => null)
    const message = body?.detail ?? `Request failed (${response.status})`
    throw new Error(message)
  }

  // 204 No Content (e.g. a DELETE) has no body to parse.
  if (response.status === 204) {
    return undefined as T
  }
  return response.json() as Promise<T>
}

export function listSessions(): Promise<SessionSummary[]> {
  return request('/sessions')
}

export function getSession(sessionId: string): Promise<SessionDetail> {
  return request(`/sessions/${sessionId}`)
}

export function getLeaderboard(sessionId: string): Promise<Leaderboard> {
  return request(`/sessions/${sessionId}/leaderboard`)
}

export function getDriverStats(sessionId: string): Promise<DriverStats[]> {
  return request(`/sessions/${sessionId}/stats`)
}

export function getProgression(sessionId: string): Promise<DriverProgression[]> {
  return request(`/sessions/${sessionId}/progression`)
}

export function uploadSession(file: File): Promise<SessionUploadResponse> {
  // multipart/form-data — the browser sets the Content-Type header itself.
  const form = new FormData()
  form.append('file', file)
  return request('/sessions/upload', { method: 'POST', body: form })
}

export function deleteSession(sessionId: string): Promise<void> {
  return request(`/sessions/${sessionId}`, { method: 'DELETE' })
}
