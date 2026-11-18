import { useMemo, useState } from 'react'
import type {
  DriverProgression,
  DriverStats,
  LeaderboardEntry,
} from '../api/types'
import { computeDriverView } from '../lib/driverStats'
import { computeLapPositions } from '../lib/positions'
import { LapChart } from './LapChart'
import { PositionChart } from './PositionChart'
import { LapTable } from './driver/LapTable'
import { StatGrid } from './driver/StatGrid'

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

  const positions = lapPositions.get(reg) ?? []
  // The stats and per-lap position changes come from a pure function, so this
  // component only has to arrange the pieces on screen.
  const view = computeDriverView(driver, driverStats, boardEntry, positions)

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

      <StatGrid stats={view.stats} />

      <div className="chart-panel">
        <h3 className="panel-title">Lap Time</h3>
        <LapChart drivers={[driver]} height={300} />
      </div>

      <div className="chart-panel">
        <h3 className="panel-title">Track Position</h3>
        <PositionChart positions={positions} height={300} />
      </div>

      <LapTable
        laps={driver.laps}
        outliers={view.outliers}
        positionByLap={view.positionByLap}
        deltaByLap={view.deltaByLap}
      />
    </div>
  )
}
