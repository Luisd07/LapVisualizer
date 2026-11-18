import type { DriverProgression } from '../../api/types'

type DriverSelectProps = {
  drivers: DriverProgression[]
  value: string
  onChange: (reg: string) => void
}

/** The "Follow driver" dropdown. */
export function DriverSelect({ drivers, value, onChange }: DriverSelectProps) {
  // A controlled input: React state (`value`) is the single source of truth,
  // and the parent updates it through the `onChange` callback prop.
  return (
    <div className="driver-toolbar">
      <label className="field-label" htmlFor="driver-pick">
        Follow driver
      </label>
      <select
        id="driver-pick"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {/* `key` lets React match each <option> to its driver between renders. */}
        {drivers.map((d) => (
          <option key={d.reg_number} value={d.reg_number}>
            #{d.number} {d.driver_name}
          </option>
        ))}
      </select>
    </div>
  )
}
