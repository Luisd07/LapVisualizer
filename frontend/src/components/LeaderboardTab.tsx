import type { Leaderboard, LeaderboardEntry } from '../api/types'
import { formatDuration, formatGap, formatLapTime, formatRaceGap } from '../lib/format'

type LeaderboardTabProps = {
  leaderboard: Leaderboard
}

/**
 * Session results, taken straight from the timing system's classification:
 * finishing order for a race, best-lap order for a practice or qualifying run.
 */
export function LeaderboardTab({ leaderboard }: LeaderboardTabProps) {
  const { session_type, entries } = leaderboard

  if (entries.length === 0) {
    return <p className="state">No classified drivers in this session.</p>
  }

  return session_type === 'race' ? (
    <RaceResults entries={entries} />
  ) : (
    <PracticeResults entries={entries} />
  )
}

/** Finishing order for a race — ranked by the `$G` classification. */
function RaceResults({ entries }: { entries: LeaderboardEntry[] }) {
  return (
    <div className="table-wrap">
      {/* `table-timing` styles this as a broadcast timing tower with a
          podium-coloured position column. */}
      <table className="data-table table-timing">
        <thead>
          <tr>
            <th>Pos</th>
            <th>#</th>
            <th>Driver</th>
            <th>Class</th>
            <th>Laps</th>
            <th>Total time</th>
            <th>Gap</th>
            <th>Best lap (official)</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry, index) => (
            <tr key={entry.reg_number}>
              <td className="num">{entry.position}</td>
              <td className="num">{entry.number}</td>
              <td>{entry.driver_name}</td>
              <td>{entry.race_class ?? '—'}</td>
              <td className="num">{entry.laps_completed ?? entry.lap_count}</td>
              <td className="num">
                {entry.total_time_seconds != null
                  ? formatDuration(entry.total_time_seconds)
                  : '—'}
              </td>
              <td className="num">
                {formatRaceGap(entry.gap_to_leader, entry.laps_down, index === 0)}
              </td>
              <td className="num accent">
                {entry.official_best_lap_time != null ? formatLapTime(entry.official_best_lap_time) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/** Best-lap order for a practice or qualifying session — the `$H` classification. */
function PracticeResults({ entries }: { entries: LeaderboardEntry[] }) {
  return (
    <div className="table-wrap">
      {/* `table-best` adds the purple session-best flag: these rows are
          ranked by best lap, so the leader holds the fastest lap. */}
      <table className="data-table table-timing table-best">
        <thead>
          <tr>
            <th>Pos</th>
            <th>#</th>
            <th>Driver</th>
            <th>Class</th>
            <th>Best lap (official)</th>
            <th>On lap</th>
            <th>Laps</th>
            <th>Gap</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.reg_number}>
              <td className="num">{entry.position}</td>
              <td className="num">{entry.number}</td>
              <td>{entry.driver_name}</td>
              <td>{entry.race_class ?? '—'}</td>
              <td className="num accent">
                {entry.official_best_lap_time != null ? formatLapTime(entry.official_best_lap_time) : '—'}
              </td>
              <td className="num">{entry.official_best_lap_number ?? '—'}</td>
              <td className="num">{entry.lap_count}</td>
              <td className="num">{formatGap(entry.gap_to_leader ?? 0)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
