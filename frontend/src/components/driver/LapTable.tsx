import type { ProgressionLap } from '../../api/types'
import { formatDuration, formatGap, formatLapTime } from '../../lib/format'

type LapTableProps = {
  laps: ProgressionLap[]
  outliers: Set<number>
  positionByLap: Map<number, number>
  deltaByLap: Map<number, number>
}

/** Every lap for one driver, with running position and Best/Outlier tags. */
export function LapTable({ laps, outliers, positionByLap, deltaByLap }: LapTableProps) {
  return (
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
          {laps.map((lap) => (
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
