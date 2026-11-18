import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { deleteSession, listSessions } from '../api/client'
import type { SessionSummary } from '../api/types'
import { SessionsPage } from './SessionsPage'

// Replace the real API module with auto-mocks so no network is touched.
vi.mock('../api/client')

const session: SessionSummary = {
  session_id: 's1',
  session_name: 'Sunday Race',
  run_number: null,
  track_name: 'Brands Hatch',
  driver_count: 10,
  total_laps: 100,
  uploaded_at: '2026-01-01T12:00:00Z',
}

function renderPage() {
  render(
    <MemoryRouter>
      <SessionsPage />
    </MemoryRouter>,
  )
}

describe('SessionsPage delete', () => {
  beforeEach(() => {
    vi.mocked(listSessions).mockResolvedValue([session])
  })

  it('shows an alert and keeps the card when delete fails', async () => {
    vi.mocked(deleteSession).mockRejectedValue(new Error('Server exploded'))
    renderPage()

    fireEvent.click(await screen.findByRole('button', { name: 'Delete' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Server exploded')
    expect(screen.getByText('Sunday Race')).toBeInTheDocument()
  })

  it('removes the card when delete succeeds', async () => {
    vi.mocked(deleteSession).mockResolvedValue(undefined)
    renderPage()

    fireEvent.click(await screen.findByRole('button', { name: 'Delete' }))

    await waitFor(() => expect(screen.queryByText('Sunday Race')).not.toBeInTheDocument())
  })
})
