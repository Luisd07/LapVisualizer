import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { Leaderboard } from '../api/types'
import { LeaderboardTab } from './LeaderboardTab'

const leaderboard: Leaderboard = {
  session_type: 'race',
  entries: [
    {
      position: 1,
      reg_number: 'A1',
      number: '7',
      driver_name: 'Ada Racer',
      race_class: null,
      lap_count: 10,
      laps_completed: 10,
      laps_down: null,
      gap_to_leader: null,
      total_time_seconds: 600,
      official_best_lap_number: 4,
      official_best_lap_time: 45.231,
    },
  ],
}

describe('LeaderboardTab', () => {
  it('renders the official best lap column and a formatted time', () => {
    render(<LeaderboardTab leaderboard={leaderboard} />)
    expect(
      screen.getByRole('columnheader', { name: 'Best lap (official)' }),
    ).toBeInTheDocument()
    expect(screen.getByText('45.231')).toBeInTheDocument()
  })
})
