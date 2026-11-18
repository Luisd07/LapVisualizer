import { describe, expect, it } from 'vitest'
import { makeDriver, makeLap } from '../test/fixtures'
import { computeLapPositions } from './positions'

describe('computeLapPositions', () => {
  it('ranks drivers by cumulative time on each lap', () => {
    const result = computeLapPositions([
      makeDriver('A', [makeLap(1, 50), makeLap(2, 105)]),
      makeDriver('B', [makeLap(1, 52), makeLap(2, 101)]),
    ])
    expect(result.get('A')).toEqual([
      { lap_number: 1, position: 1 },
      { lap_number: 2, position: 2 },
    ])
    expect(result.get('B')).toEqual([
      { lap_number: 1, position: 2 },
      { lap_number: 2, position: 1 },
    ])
  })

  it('only ranks drivers who completed the lap and sorts out-of-order laps', () => {
    const result = computeLapPositions([
      makeDriver('A', [makeLap(2, 100), makeLap(1, 50)]),
      makeDriver('B', [makeLap(1, 55)]),
    ])
    expect(result.get('A')?.map((p) => p.lap_number)).toEqual([1, 2])
    expect(result.get('B')).toEqual([{ lap_number: 1, position: 2 }])
  })

  it('returns an empty map for an empty field', () => {
    expect(computeLapPositions([]).size).toBe(0)
  })
})
