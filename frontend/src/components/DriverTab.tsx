import { useMemo, useState } from 'react'
import type {
  DriverProgression,
  DriverStats,
  LeaderboardEntry,
} from '../api/types'
import { formatDuration, formatGap, formatLapTime } from '../lib/format'
import { computeLapPositions } from '../lib/positions'
import { LapChart } from './LapChart'
import { PositionChart } from './PositionChart'

type DriverTabProps = {
  progression: DriverProgression[]
  stats: DriverStats[]
  leaderboard: LeaderboardEntry[]
}

/** Follow one driver: pick them, see their stats, charts, and every lap. */
export function DriverTab({ progression, stats, leaderboard }: DriverTabProps) {
  const drivers = [...progression].sort((a, b) =>
    a.driver_name.localeCompare(b.driver_name),
  )

  const [reg, setReg] = useState<string>(() => drivers[0]?.reg_number ?? '')

  // Running position per lap for the whole field — derived once, since one
  // driver's position depends on everyone else's elapsed times.
  const lapPositions = useMemo(
    () => computeLapPositions(progression),
    [progression],
  )

  const driver = progression.find((d) => d.reg_number === reg)
  const driverStats = stats.find((s) => s.reg_number === reg)
  const boardEntry = leaderboard.find((e) => e.reg_number === reg)

  if (!driver) {
    return <p className="state">No drivers in this session.</p>
  }

  const outliers = new Set(driverStats?.outlier_lap_numbers ?? [])

  // This driver's position after each lap, plus how far it moved since the
  // lap before — both keyed by lap number for quick lookup in the table.
  const positions = lapPositions.get(reg) ?? []
  const positionByLap = new Map(positions.map((p) => [p.lap_number, p.position]))
  const deltaByLap = new Map<number, number>()
  positions.forEach((entry, index) => {
    if (index > 0) {
      // A drop in position number means places gained: previous − current.
      deltaByLap.set(entry.lap_number, positions[index - 1].position - entry.position)
    }
  })

  return (
    <div className="driver-view">
      <div className="driver-toolbar">
        <label className="field-label" htmlFor="driver-pick">
          Follow driver
        </label>
        <select
          id="driver-pick"
          value={reg}
          onChange={(event) => setReg(event.target.value)}
        >
          {drivers.map((d) => (
            <option key={d.reg_number} value={d.reg_number}>
              #{d.number} {d.driver_name}
            </option>
          ))}
        </select>
      </div>

      <div className="stat-grid">
        <Stat
          label="Fastest lap"
          value={driver.fastest_lap_time != null ? formatLapTime(driver.fastest_lap_time) : '—'}
          accent
        />
        <Stat label="Position" value={boardEntry ? `P${boardEntry.position}` : '—'} />
        <Stat label="Laps" value={String(driver.laps.length)} />
        <Stat
          label="Mean lap"
          value={driverStats ? formatLapTime(driverStats.mean_lap_time) : '—'}
        />
        <Stat
          label="Std dev"
          value={driverStats ? `${driverStats.std_dev_seconds.toFixed(3)}s` : '—'}
        />
        <Stat label="Outlier laps" value={String(outliers.size)} />
      </div>

      <div className="chart-panel">
        <h3 className="panel-title">Lap Time</h3>
        <LapChart drivers={[driver]} height={300} />
      </div>

      <div className="chart-panel">
        <h3 className="panel-title">Track Position</h3>
        <PositionChart positions={positions} height={300} />
      </div>

      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Lap</th>
              <th>Pos</th>
              <th>Lap time</th>
              <th>Gap to best</th>
              <th>Total time</th>
              <th>Note</th>
            </tr>
          </thead>
          <tbody>
            {driver.laps.map((lap) => (
              <tr key={lap.lap_number}>
                <td className="num">{lap.lap_number}</td>
                <td className="num">
                  <PositionCell
                    position={positionByLap.get(lap.lap_number)}
                    delta={deltaByLap.get(lap.lap_number)}
                  />
                </td>
                <td className={lap.is_personal_best ? 'num accent' : 'num'}>
                  {formatLapTime(lap.lap_time_seconds)}
                </td>
                <td className="num">{formatGap(lap.gap_to_personal_best)}</td>
                <td className="num">{formatDuration(lap.total_time_seconds)}</td>
                <td>
                  {lap.is_personal_best && <span className="tag tag-best">Best</span>}
                  {outliers.has(lap.lap_number) && (
                    <span className="tag tag-out">Outlier</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

type StatProps = {
  label: string
  value: string
  accent?: boolean
}

/** A single labelled stat in the summary grid. */
function Stat({ label, value, accent }: StatProps) {
  return (
    <div className="stat">
      <span className="stat-label">{label}</span>
      <span className={accent ? 'stat-value accent' : 'stat-value'}>{value}</span>
    </div>
  )
}

type PositionCellProps = {
  position: number | undefined
  delta: number | undefined
}

/** A lap's running position, with a coloured ▲/▼ change since the lap before. */
function PositionCell({ position, delta }: PositionCellProps) {
  if (position == null) return <>—</>
  return (
    <span className="pos-cell">
      P{position}
      {delta != null && delta !== 0 && (
        <span className={delta > 0 ? 'pos-delta pos-gain' : 'pos-delta pos-loss'}>
          {delta > 0 ? '▲' : '▼'}
          {Math.abs(delta)}
        </span>
      )}
    </span>
  )
}
