import type { DriverStats } from '../api/types'
import { formatLapTime } from '../lib/format'

type StatsTabProps = {
  stats: DriverStats[]
}

/** Per-driver consistency statistics, fastest best-lap first. */
export function StatsTab({ stats }: StatsTabProps) {
  if (stats.length === 0) {
    return <p className="state">No timed laps in this session.</p>
  }

  const sorted = [...stats].sort((a, b) => a.fastest_lap_time - b.fastest_lap_time)

  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Driver</th>
            <th>Laps</th>
            <th>Fastest lap</th>
            <th>Mean</th>
            <th>Median</th>
            <th>Worst</th>
            <th>Std dev</th>
            <th>Outliers</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => (
            <tr key={row.reg_number}>
              <td className="num">{row.number}</td>
              <td>{row.driver_name}</td>
              <td className="num">{row.lap_count}</td>
              <td className="num accent">{formatLapTime(row.fastest_lap_time)}</td>
              <td className="num">{formatLapTime(row.mean_lap_time)}</td>
              <td className="num">{formatLapTime(row.median_lap_time)}</td>
              <td className="num">{formatLapTime(row.worst_lap_time)}</td>
              <td className="num">{row.std_dev_seconds.toFixed(3)}</td>
              <td className="num">{row.outlier_lap_numbers.length}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
