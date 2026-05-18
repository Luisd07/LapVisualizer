import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { DriverProgression } from '../api/types'
import { chartColor } from '../lib/colors'
import { formatLapTime } from '../lib/format'

type LapChartProps = {
  /** Drivers to plot — one line each, coloured by array order. */
  drivers: DriverProgression[]
  height?: number
}

/** A line chart of lap time (y) against lap number (x), one line per driver. */
export function LapChart({ drivers, height = 420 }: LapChartProps) {
  if (drivers.length === 0) {
    return <p className="state">Select one or more drivers to plot.</p>
  }

  // Recharts wants one row per x-value, so reshape the per-driver lap lists
  // into rows keyed by lap number: [{ lap: 1, "11": 45.2, "22": 46.0 }, ...].
  const maxLap = Math.max(...drivers.map((d) => d.laps.length))
  const rows: Array<Record<string, number>> = []
  for (let lap = 1; lap <= maxLap; lap += 1) {
    const row: Record<string, number> = { lap }
    for (const driver of drivers) {
      const match = driver.laps.find((l) => l.lap_number === lap)
      if (match) row[driver.reg_number] = match.lap_time_seconds
    }
    rows.push(row)
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={rows} margin={{ top: 8, right: 20, bottom: 4, left: 4 }}>
        <CartesianGrid stroke="#232934" strokeDasharray="2 5" />
        <XAxis dataKey="lap" stroke="#3a414f" tick={{ fill: '#98a2b3', fontSize: 12 }} />
        {/* Zoom the y-axis to the actual lap-time range (with 1s of padding)
            instead of starting at zero, so small differences are visible. */}
        <YAxis
          stroke="#3a414f"
          tick={{ fill: '#98a2b3', fontSize: 12 }}
          tickFormatter={(value) => formatLapTime(Number(value))}
          width={66}
          domain={['dataMin - 1', 'dataMax + 1']}
          allowDecimals
        />
        <Tooltip
          cursor={{ stroke: '#353d4b', strokeWidth: 1 }}
          contentStyle={{
            background: '#0c0f15',
            border: '1px solid #353d4b',
            borderRadius: 4,
            fontSize: 13,
            fontFamily: "'Spline Sans Mono', ui-monospace, monospace",
          }}
          labelStyle={{
            color: '#98a2b3',
            fontFamily: "'Saira Condensed', sans-serif",
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
          }}
          labelFormatter={(lap) => `Lap ${lap}`}
          formatter={(value) => formatLapTime(Number(value))}
        />
        {drivers.map((driver, index) => (
          <Line
            key={driver.reg_number}
            type="monotone"
            dataKey={driver.reg_number}
            name={`#${driver.number} ${driver.driver_name}`}
            stroke={chartColor(index)}
            strokeWidth={2.25}
            dot={false}
            activeDot={{ r: 4, strokeWidth: 0 }}
            connectNulls
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
