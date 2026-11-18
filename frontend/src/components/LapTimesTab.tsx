import { useState } from 'react'
import type { DriverProgression } from '../api/types'
import { chartColor } from '../lib/colors'
import { formatLapTime } from '../lib/format'
import { LapChart } from './LapChart'

type LapTimesTabProps = {
  progression: DriverProgression[]
}

/** How many drivers to plot by default (the fastest few). */
const DEFAULT_COUNT = 5

/** Lap-time chart with a scrollable, selectable driver list (the legend). */
export function LapTimesTab({ progression }: LapTimesTabProps) {
  // Drivers that actually set laps, fastest best-lap first.
  const drivers = [...progression]
    .filter((d) => d.laps.length > 0)
    .sort((a, b) => (a.fastest_lap_time ?? Infinity) - (b.fastest_lap_time ?? Infinity))

  const [selected, setSelected] = useState<Set<string>>(
    () => new Set(drivers.slice(0, DEFAULT_COUNT).map((d) => d.reg_number)),
  )

  function toggle(reg: string) {
    setSelected((current) => {
      const next = new Set(current)
      if (next.has(reg)) next.delete(reg)
      else next.add(reg)
      return next
    })
  }

  // Drivers actually plotted — their order fixes both the line colour and
  // the swatch colour, keeping the chart and the list in sync.
  const plotted = drivers.filter((d) => selected.has(d.reg_number))

  return (
    <div className="laptimes">
      <aside className="driver-list">
        {drivers.map((driver) => {
          const on = selected.has(driver.reg_number)
          const index = plotted.findIndex((d) => d.reg_number === driver.reg_number)
          return (
            <button
              key={driver.reg_number}
              className={on ? 'driver-row on' : 'driver-row'}
              onClick={() => toggle(driver.reg_number)}
            >
              <span
                className="swatch"
                style={{
                  background: on ? chartColor(index) : 'var(--border-strong)',
                }}
              />
              <span className="driver-row-name">
                #{driver.number} {driver.driver_name}
              </span>
              <span className="driver-row-time">
                {driver.fastest_lap_time != null
                  ? formatLapTime(driver.fastest_lap_time)
                  : '—'}
              </span>
            </button>
          )
        })}
      </aside>
      <div className="chart-panel">
        <LapChart drivers={plotted} />
      </div>
    </div>
  )
}
