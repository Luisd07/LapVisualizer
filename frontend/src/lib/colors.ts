/**
 * Distinct line colours for charts, cycled by index.
 *
 * Tuned for the dark "KartChaser" theme: every hue is bright enough to
 * read on the near-black panel, and the series leads with KartChaser blue.
 */
export const CHART_COLORS = [
  '#5b8cff', // KartChaser blue
  '#b98bff', // violet
  '#3ee089', // green
  '#ffb23e', // amber
  '#ff6d8a', // coral
  '#36d6e6', // cyan
  '#ff8a4c', // orange
  '#9d7bff', // indigo
  '#7ee787', // lime
  '#79b8ff', // sky
]

/** Pick a colour for series `index`, wrapping around the palette. */
export function chartColor(index: number): string {
  return CHART_COLORS[index % CHART_COLORS.length]
}
