// Minimal tone system utilities for the Velinor frontend.
// Provides formatting and simple unlock/ending rules used by the UI.

export type ToneStats = {
  trust: number
  observation: number
  narrativePresence: number
  empathy: number
}

export function formatToneStats(stats: ToneStats) {
  return {
    trust: Math.round(stats.trust),
    observation: Math.round(stats.observation),
    narrativePresence: Math.round(stats.narrativePresence),
    empathy: Math.round(stats.empathy),
  }
}

export function getToneTier(value: number): string {
  if (value < 30) return 'Poor'
  if (value < 50) return 'Weak'
  if (value < 70) return 'Good'
  if (value < 85) return 'Strong'
  return 'Masterful'
}

// Simple unlock rules: return glyph ids likely to be unlocked next
export function getUnlockableGlyphs(stats: ToneStats): string[] {
  const candidates: string[] = []
  if (stats.empathy >= 65) candidates.push('glyph_compassion')
  if (stats.trust >= 60) candidates.push('glyph_anchor')
  if (stats.observation >= 60) candidates.push('glyph_observe')
  if (stats.narrativePresence >= 70) candidates.push('glyph_presence')
  return candidates
}

// Determine which endings are accessible based on tone thresholds
export function getAccessibleEndings(stats: ToneStats): string[] {
  const endings: string[] = []
  if (stats.empathy >= 70 && stats.trust >= 60) endings.push('Saori_Peace')
  if (stats.trust >= 80 && stats.narrativePresence >= 60) endings.push('Velinor_Ascend')
  if (stats.observation >= 75) endings.push('Archivist_Reveal')
  if (endings.length === 0) endings.push('Common_Path')
  return endings
}

export function getAccessibleGlyphs(stats: ToneStats): string[] {
  return getUnlockableGlyphs(stats)
}

export default {
  formatToneStats,
  getToneTier,
  getUnlockableGlyphs,
  getAccessibleEndings,
}
