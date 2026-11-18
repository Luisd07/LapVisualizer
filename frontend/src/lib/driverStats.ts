/** Pure maths behind the Driver tab: summary stats and per-lap position changes. */

import type {
  DriverProgression,
  DriverStats,
  LeaderboardEntry,
} from '../api/types'
import { formatLapTime } from './format'
import type { LapPosition } from './positions'

/** One labelled value in the summary grid. */
export type StatItem = {
  label: string
  value: string
  accent?: boolean
}

export type DriverView = {
  stats: StatItem[]
  outliers: Set<number>
  positionByLap: Map<number, number>
  /** Places gained (+) or lost (−) versus the lap before, keyed by lap number. */
  deltaByLap: Map<number, number>
}

/**
 * Work out everything the Driver tab displays for one driver, so the
 * components stay purely presentational. Missing stats/classification show `—`.
 */
export function computeDriverView(
  driver: DriverProgression,
  driverStats: DriverStats | undefined,
  boardEntry: LeaderboardEntry | undefined,
  positions: LapPosition[],
): DriverView {
  const outliers = new Set(driverStats?.outlier_lap_numbers ?? [])

  const positionByLap = new Map(positions.map((p) => [p.lap_number, p.position]))
  const deltaByLap = new Map<number, number>()
  positions.forEach((entry, index) => {
    if (index > 0) {
      // A drop in position number means places gained: previous − current.
      deltaByLap.set(entry.lap_number, positions[index - 1].position - entry.position)
    }
  })

  const stats: StatItem[] = [
    {
      label: 'Fastest lap',
      value: driver.fastest_lap_time != null ? formatLapTime(driver.fastest_lap_time) : '—',
      accent: true,
    },
    { label: 'Position', value: boardEntry ? `P${boardEntry.position}` : '—' },
    { label: 'Laps', value: String(driver.laps.length) },
    {
      label: 'Mean lap',
      value: driverStats ? formatLapTime(driverStats.mean_lap_time) : '—',
    },
    {
      label: 'Std dev',
      value: driverStats ? `${driverStats.std_dev_seconds.toFixed(3)}s` : '—',
    },
    { label: 'Outlier laps', value: String(outliers.size) },
  ]

  return { stats, outliers, positionByLap, deltaByLap }
}
