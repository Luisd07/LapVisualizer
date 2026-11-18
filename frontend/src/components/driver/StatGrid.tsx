import type { StatItem } from '../../lib/driverStats'

/** The summary grid: one labelled stat per item. */
export function StatGrid({ stats }: { stats: StatItem[] }) {
  // Props are destructured right in the signature's parameter; `stats` is
  // the one prop this component receives from its parent.
  return (
    <div className="stat-grid">
      {/* Rendering a list: each item needs a stable, unique `key`. */}
      {stats.map(({ label, value, accent }) => (
        <div key={label} className="stat">
          <span className="stat-label">{label}</span>
          <span className={accent ? 'stat-value accent' : 'stat-value'}>{value}</span>
        </div>
      ))}
    </div>
  )
}
