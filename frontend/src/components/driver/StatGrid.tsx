import type { StatItem } from '../../lib/driverStats'

/** The summary grid: one labelled stat per item. */
export function StatGrid({ stats }: { stats: StatItem[] }) {
  return (
    <div className="stat-grid">
      {stats.map(({ label, value, accent }) => (
        <div key={label} className="stat">
          <span className="stat-label">{label}</span>
          <span className={accent ? 'stat-value accent' : 'stat-value'}>{value}</span>
        </div>
      ))}
    </div>
  )
}
