import { describe, expect, it } from 'vitest'
import { formatGap, formatLapTime, formatRaceGap } from './format'

describe('formatLapTime', () => {
  it('shows seconds only under a minute', () => {
    expect(formatLapTime(45.231)).toBe('45.231')
  })
  it('switches to M:SS.mmm past a minute', () => {
    expect(formatLapTime(65.231)).toBe('1:05.231')
  })
})

describe('formatGap', () => {
  it('prefixes a positive gap with +', () => {
    expect(formatGap(1.234)).toBe('+1.234')
  })
  it('shows a dash when there is no gap', () => {
    expect(formatGap(0)).toBe('—')
  })
})

describe('formatRaceGap', () => {
  it('labels the leader', () => {
    expect(formatRaceGap(null, null, true)).toBe('Leader')
  })
  it('shows laps down, singular and plural', () => {
    expect(formatRaceGap(null, 1, false)).toBe('+1 lap')
    expect(formatRaceGap(null, 2, false)).toBe('+2 laps')
  })
  it('shows a time gap on the lead lap', () => {
    expect(formatRaceGap(11.5, 0, false)).toBe('+11.500')
  })
  it('shows a dash when nothing can be compared', () => {
    expect(formatRaceGap(null, null, false)).toBe('—')
  })
})
