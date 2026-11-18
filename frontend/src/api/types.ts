/**
 * Named aliases for the API response types.
 *
 * The shapes are generated from the FastAPI OpenAPI schema (`npm run gen:api`
 * writes `schema.gen.ts`), so field names are snake_case exactly as the
 * backend sends them. Do not hand-write response shapes here.
 */
import type { components } from './schema.gen'

type Schemas = components['schemas']

/**
 * The backend always serializes fields that have defaults, but OpenAPI marks
 * them optional. `Required` restores what the API actually sends.
 */

export type DriverSummary = Schemas['DriverSummary']
export type SessionSummary = Schemas['SessionSummary']
export type SessionDetail = Schemas['SessionDetail']
export type SessionUploadResponse = Schemas['SessionUploadResponse']
export type LeaderboardEntry = Required<Schemas['LeaderboardEntry']>
export type Leaderboard = Required<Omit<Schemas['Leaderboard'], 'entries'>> & {
  entries: LeaderboardEntry[]
}
export type DriverStats = Required<Schemas['DriverStats']>
export type ProgressionLap = Schemas['ProgressionLap']
export type DriverProgression = Required<Schemas['DriverProgression']>

/** Whether a session is ranked by finishing order or by best lap. */
export type SessionType = Schemas['SessionType']
