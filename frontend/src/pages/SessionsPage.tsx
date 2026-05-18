import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { deleteSession, listSessions } from '../api/client'
import type { SessionSummary } from '../api/types'
import { formatDateTime } from '../lib/format'

/** Page 2: a grid of stored sessions, each linking to its dashboard. */
export function SessionsPage() {
  const [sessions, setSessions] = useState<SessionSummary[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // useEffect with an empty dependency array `[]` runs once, just after the
  // component first mounts — the place to kick off data loading.
  useEffect(() => {
    listSessions()
      .then(setSessions)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load'))
      .finally(() => setLoading(false))
  }, [])

  async function handleDelete(sessionId: string) {
    await deleteSession(sessionId)
    // Remove the deleted card from state so the grid re-renders without it.
    setSessions((current) => current.filter((s) => s.session_id !== sessionId))
  }

  if (loading) return <p className="state">Loading sessions…</p>
  if (error) {
    return (
      <p className="state state-error" role="alert">
        {error}
      </p>
    )
  }

  return (
    <section>
      <div className="page-header">
        <h2>Sessions</h2>
        <p>
          {sessions.length} stored {sessions.length === 1 ? 'session' : 'sessions'}
        </p>
      </div>

      {sessions.length === 0 ? (
        <p className="state">No sessions yet — upload a log to get started.</p>
      ) : (
        <div className="session-grid">
          {sessions.map((session) => (
            <article key={session.session_id} className="session-card">
              <Link
                to={`/sessions/${session.session_id}`}
                className="session-card-name"
              >
                {session.session_name}
              </Link>
              <span className="session-card-track">
                {session.track_name ?? 'Unknown track'}
              </span>
              <div className="session-card-stats">
                <span className="badge">
                  <strong>{session.driver_count}</strong> drivers
                </span>
                <span className="badge">
                  <strong>{session.total_laps}</strong> laps
                </span>
              </div>
              <div className="session-card-foot">
                <span>{formatDateTime(session.uploaded_at)}</span>
                <button
                  className="btn-ghost"
                  onClick={() => handleDelete(session.session_id)}
                >
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}
