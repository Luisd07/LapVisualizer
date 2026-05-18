/** Lap-by-lap running-position maths, derived from the field's lap times. */

import type { DriverProgression } from '../api/types'

/** A driver's running position after completing one lap. */
export type LapPosition = {
  lap_number: number
  position: number
}

/**
 * Compute every driver's running position, lap by lap.
 *
 * At each lap N, the drivers that have completed lap N are ranked by their
 * cumulative `total_time_seconds` — whoever reached lap N in the least total
 * time leads it. This is the standard way a lap chart is derived from timing
 * data, and gives true running order for a race.
 *
 * Returns a map of `reg_number` → that driver's positions, in lap order.
 */
export function computeLapPositions(
  progression: DriverProgression[],
): Map<string, LapPosition[]> {
  // Group every (driver, lap) pair by lap number.
  const fieldByLap = new Map<number, { reg: string; elapsed: number }[]>()
  for (const driver of progression) {
    for (const lap of driver.laps) {
      const field = fieldByLap.get(lap.lap_number) ?? []
      field.push({ reg: driver.reg_number, elapsed: lap.total_time_seconds })
      fieldByLap.set(lap.lap_number, field)
    }
  }

  // Rank each lap's field by elapsed time, then record everyone's position.
  const positions = new Map<string, LapPosition[]>()
  for (const [lap_number, field] of fieldByLap) {
    field.sort((a, b) => a.elapsed - b.elapsed)
    field.forEach(({ reg }, index) => {
      const list = positions.get(reg) ?? []
      list.push({ lap_number, position: index + 1 })
      positions.set(reg, list)
    })
  }

  // A driver's laps may have been grouped out of order — sort each list.
  for (const list of positions.values()) {
    list.sort((a, b) => a.lap_number - b.lap_number)
  }
  return positions
}
