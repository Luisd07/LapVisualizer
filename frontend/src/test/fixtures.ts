import type { DriverProgression, ProgressionLap } from '../api/types'

export function makeLap(lap_number: number, total_time_seconds: number): ProgressionLap {
  return {
    lap_number,
    lap_time_seconds: 50,
    total_time_seconds,
    gap_to_personal_best: 0,
    is_personal_best: false,
  }
}

export function makeDriver(reg_number: string, laps: ProgressionLap[]): DriverProgression {
  return {
    reg_number,
    driver_name: `Driver ${reg_number}`,
    number: reg_number,
    race_class: null,
    fastest_lap_time: 50,
    laps,
  }
}
