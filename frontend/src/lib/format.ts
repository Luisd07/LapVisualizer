/** Time and number formatting helpers shared across the UI. */

/**
 * Format a lap time (in seconds) for display: `45.231`, or `1:05.231` once
 * it passes a minute. Lap times are short, so seconds-only is the common case.
 */
export function formatLapTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remainder = seconds - minutes * 60
  if (minutes === 0) return remainder.toFixed(3)
  return `${minutes}:${remainder.toFixed(3).padStart(6, '0')}`
}

/** Format a longer duration (a session or total time) as `M:SS.mmm`. */
export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remainder = seconds - minutes * 60
  return `${minutes}:${remainder.toFixed(3).padStart(6, '0')}`
}

/** Format a gap to the leader/best: `+1.234`, or `—` when there is none. */
export function formatGap(seconds: number): string {
  if (seconds <= 0) return '—'
  return `+${seconds.toFixed(3)}`
}

/**
 * Format a race driver's gap to the winner: `Leader` for P1, a time
 * (`+11.500`) for a car on the lead lap, a lap count (`+1 lap`) for a lapped
 * car, or `—` when the classification gives nothing to compare.
 */
export function formatRaceGap(
  gapSeconds: number | null,
  lapsDown: number | null,
  isLeader: boolean,
): string {
  if (isLeader) return 'Leader'
  if (lapsDown != null && lapsDown > 0) {
    return `+${lapsDown} lap${lapsDown === 1 ? '' : 's'}`
  }
  if (gapSeconds != null && gapSeconds > 0) return `+${gapSeconds.toFixed(3)}`
  return '—'
}

/** Format an ISO timestamp as a short, local date-and-time string. */
export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}
