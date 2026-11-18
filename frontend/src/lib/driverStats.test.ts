import { describe, expect, it } from 'vitest'
import { makeDriver, makeLap } from '../test/fixtures'
import { computeDriverView } from './driverStats'

describe('computeDriverView', () => {
  const driver = makeDriver('A', [makeLap(1, 50), makeLap(2, 100), makeLap(3, 150)])
  const positions = [
    { lap_number: 1, position: 3 },
    { lap_number: 2, position: 1 },
    { lap_number: 3, position: 2 },
  ]

  it('computes places gained and lost versus the previous lap', () => {
    const view = computeDriverView(driver, undefined, undefined, positions)
    expect(view.positionByLap.get(2)).toBe(1)
    expect(view.deltaByLap.has(1)).toBe(false)
    expect(view.deltaByLap.get(2)).toBe(2)
    expect(view.deltaByLap.get(3)).toBe(-1)
  })

  it('falls back to dashes without stats or classification', () => {
    const { stats } = computeDriverView(driver, undefined, undefined, positions)
    const byLabel = Object.fromEntries(stats.map((s) => [s.label, s.value]))
    expect(byLabel['Fastest lap']).toBe('50.000')
    expect(byLabel['Position']).toBe('—')
    expect(byLabel['Mean lap']).toBe('—')
    expect(byLabel['Std dev']).toBe('—')
    expect(byLabel['Laps']).toBe('3')
    expect(byLabel['Outlier laps']).toBe('0')
  })
})
