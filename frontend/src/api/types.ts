/**
 * Named aliases for the API response types.
 *
 * The shapes are generated from the FastAPI OpenAPI schema (`npm run gen:api`
 * writes `schema.gen.ts`), so field names are snake_case exactly as the
 * backend sends them. Do not hand-write response shapes here.
 */
import type { components } from './schema.gen'

type Schemas = components['schemas']

export type DriverSummary = Schemas['DriverSummary']
export type SessionSummary = Schemas['SessionSummary']
export type SessionDetail = Schemas['SessionDetail']
export type SessionUploadResponse = Schemas['SessionUploadResponse']
export type LeaderboardEntry = Schemas['LeaderboardEntry']
export type Leaderboard = Schemas['Leaderboard']
export type DriverStats = Schemas['DriverStats']
export type ProgressionLap = Schemas['ProgressionLap']
export type DriverProgression = Schemas['DriverProgression']

/** Whether a session is ranked by finishing order or by best lap. */
export type SessionType = Schemas['SessionType']
