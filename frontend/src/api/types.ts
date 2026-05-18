/**
 * TypeScript types mirroring the backend's Pydantic response schemas.
 *
 * The field names are snake_case on purpose — they match the JSON the
 * FastAPI backend actually sends, so no mapping layer is needed between
 * the API and the UI.
 */

/** A driver as listed inside a session (backend: DriverSummary). */
export type DriverSummary = {
  reg_number: string
  first_name: string
  last_name: string
  number: string
  race_class: string | null
  team: string | null
  chassis: string | null
  lap_count: number
  best_lap_time: number | null
  finish_position: number | null
}

/** A session as shown in the list view (backend: SessionSummary). */
export type SessionSummary = {
  session_id: string
  session_name: string
  run_number: number | null
  track_name: string | null
  total_laps: number
  driver_count: number
  uploaded_at: string
}

/** A full session with its drivers (backend: SessionDetail). */
export type SessionDetail = {
  session_id: string
  session_name: string
  run_number: number | null
  track_name: string | null
  track_length: number | null
  flag_status: string | null
  race_time_seconds: number | null
  time_of_day: string | null
  session_date: string | null
  total_laps: number
  driver_count: number
  uploaded_at: string
  drivers: DriverSummary[]
  warnings: string[]
}

/** The response returned right after an upload (backend: SessionUploadResponse). */
export type SessionUploadResponse = {
  session_id: string
  session_name: string
  run_number: number | null
  track_name: string | null
  total_laps: number
  driver_count: number
  uploaded_at: string
  duplicate: boolean
  warnings: string[]
}

/** Whether a session is ranked by finishing order or by best lap. */
export type SessionType = 'race' | 'practice'

/**
 * One row of a session leaderboard (backend: LeaderboardEntry).
 *
 * This mirrors the timing system's official classification, so `position` is
 * the real standing. Fields that only one session type provides are `null`
 * otherwise — e.g. `total_time_seconds` is set for races, not practices.
 */
export type LeaderboardEntry = {
  position: number
  reg_number: string
  number: string
  driver_name: string
  race_class: string | null
  lap_count: number
  best_lap_time: number | null
  best_lap_number: number | null
  laps_completed: number | null
  total_time_seconds: number | null
  gap_to_leader: number | null
  laps_down: number | null
}

/** A session's full classification (backend: Leaderboard). */
export type Leaderboard = {
  session_type: SessionType
  entries: LeaderboardEntry[]
}

/** Aggregate lap statistics for one driver (backend: DriverStats). */
export type DriverStats = {
  reg_number: string
  number: string
  driver_name: string
  race_class: string | null
  lap_count: number
  best_lap_time: number
  worst_lap_time: number
  mean_lap_time: number
  median_lap_time: number
  std_dev_seconds: number
  outlier_lap_numbers: number[]
}

/** One lap within a driver's progression (backend: ProgressionLap). */
export type ProgressionLap = {
  lap_number: number
  lap_time_seconds: number
  total_time_seconds: number
  gap_to_personal_best: number
  is_personal_best: boolean
}

/** A driver's laps in order — the data behind the lap-time charts. */
export type DriverProgression = {
  reg_number: string
  number: string
  driver_name: string
  race_class: string | null
  best_lap_time: number | null
  laps: ProgressionLap[]
}
