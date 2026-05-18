import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { LapPosition } from '../lib/positions'

type PositionChartProps = {
  /** One driver's running position after each completed lap. */
  positions: LapPosition[]
  height?: number
}

/**
 * A line chart of track position (y) against lap number (x) for one driver.
 * The y-axis is reversed so P1 sits at the top, like a real timing screen.
 */
export function PositionChart({ positions, height = 300 }: PositionChartProps) {
  if (positions.length === 0) {
    return <p className="state">No position data for this driver.</p>
  }

  // A tidy set of integer y-ticks. `axisMax` keeps a visible range even for a
  // driver who led every lap (worst === 1), so the axis never collapses.
  const worst = positions.reduce((max, p) => Math.max(max, p.position), 1)
  const axisMax = Math.max(worst, 2)
  const step = Math.max(1, Math.ceil(axisMax / 6))
  const ticks: number[] = []
  for (let p = 1; p <= axisMax; p += step) ticks.push(p)
  if (ticks[ticks.length - 1] !== axisMax) ticks.push(axisMax)

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={positions} margin={{ top: 14, right: 20, bottom: 4, left: 4 }}>
        <CartesianGrid stroke="#232934" strokeDasharray="2 5" />
        <XAxis
          dataKey="lap_number"
          stroke="#3a414f"
          tick={{ fill: '#98a2b3', fontSize: 12 }}
        />
        {/* `reversed` flips the axis so the lead position is at the top. */}
        <YAxis
          stroke="#3a414f"
          tick={{ fill: '#98a2b3', fontSize: 12 }}
          tickFormatter={(value) => `P${value}`}
          ticks={ticks}
          interval={0}
          width={48}
          reversed
          allowDecimals={false}
          domain={[1, axisMax]}
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
          formatter={(value) => [`P${value}`, 'Position']}
        />
        <Line
          type="linear"
          dataKey="position"
          name="Position"
          stroke="#5b8cff"
          strokeWidth={2.25}
          dot={{ r: 2.5, fill: '#5b8cff', strokeWidth: 0 }}
          activeDot={{ r: 4, strokeWidth: 0 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
