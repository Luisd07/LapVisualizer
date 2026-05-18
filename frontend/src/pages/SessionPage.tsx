import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import {
  getDriverStats,
  getLeaderboard,
  getProgression,
  getSession,
} from '../api/client'
import type {
  DriverProgression,
  DriverStats,
  Leaderboard,
  SessionDetail,
} from '../api/types'
import { DriverTab } from '../components/DriverTab'
import { LapTimesTab } from '../components/LapTimesTab'
import { LeaderboardTab } from '../components/LeaderboardTab'
import { StatsTab } from '../components/StatsTab'
import { formatDuration } from '../lib/format'

/** Everything the dashboard needs, fetched together up front. */
type DashboardData = {
  session: SessionDetail
  leaderboard: Leaderboard
  progression: DriverProgression[]
  stats: DriverStats[]
}

type TabId = 'leaderboard' | 'laptimes' | 'stats' | 'driver'

const TABS: { id: TabId; label: string }[] = [
  { id: 'leaderboard', label: 'Leaderboard' },
  { id: 'laptimes', label: 'Lap Times' },
  { id: 'stats', label: 'Stats' },
  { id: 'driver', label: 'Driver' },
]

/** Page 3: the tabbed analysis dashboard for a single session. */
export function SessionPage() {
  const { sessionId } = useParams<{ sessionId: string }>()

  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState<TabId>('leaderboard')

  useEffect(() => {
    if (!sessionId) return
    // All four endpoints at once. `progression` carries every driver's full
    // lap list, which is enough to drive the charts and the Driver tab.
    Promise.all([
      getSession(sessionId),
      getLeaderboard(sessionId),
      getProgression(sessionId),
      getDriverStats(sessionId),
    ])
      .then(([session, leaderboard, progression, stats]) => {
        setData({ session, leaderboard, progression, stats })
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load'))
      .finally(() => setLoading(false))
  }, [sessionId])

  if (loading) return <p className="state">Loading session…</p>
  if (error) {
    return (
      <p className="state state-error" role="alert">
        {error}
      </p>
    )
  }
  if (!data) return <p className="state">Session not found.</p>

  const { session, leaderboard, progression, stats } = data

  return (
    <section>
      <div className="page-header">
        <Link to="/sessions" className="back-link">
          ← Sessions
        </Link>
        <h2>{session.session_name}</h2>
        <div className="meta-row">
          <span className="badge badge-accent">
            {leaderboard.session_type === 'race' ? 'Race' : 'Practice'}
          </span>
          <span className="badge">{session.track_name ?? 'Unknown track'}</span>
          <span className="badge">
            <strong>{session.driver_count}</strong> drivers
          </span>
          <span className="badge">
            <strong>{session.total_laps}</strong> laps
          </span>
          {session.flag_status && <span className="badge">{session.flag_status}</span>}
          {session.race_time_seconds != null && (
            <span className="badge">
              <strong>{formatDuration(session.race_time_seconds)}</strong>
            </span>
          )}
        </div>
      </div>

      <div className="tabs">
        {TABS.map((entry) => (
          <button
            key={entry.id}
            className={entry.id === tab ? 'tab active' : 'tab'}
            onClick={() => setTab(entry.id)}
          >
            {entry.label}
          </button>
        ))}
      </div>

      <div className="tab-panel">
        {tab === 'leaderboard' && <LeaderboardTab leaderboard={leaderboard} />}
        {tab === 'laptimes' && <LapTimesTab progression={progression} />}
        {tab === 'stats' && <StatsTab stats={stats} />}
        {tab === 'driver' && (
          <DriverTab
            progression={progression}
            stats={stats}
            leaderboard={leaderboard.entries}
          />
        )}
      </div>
    </section>
  )
}
