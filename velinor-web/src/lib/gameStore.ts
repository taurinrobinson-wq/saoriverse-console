import create from 'zustand'
import { devtools } from 'zustand/middleware'

type ToneStats = {
  trust: number
  observation: number
  narrativePresence: number
  empathy: number
}

type ToneHistoryEntry = {
  statName: string
  delta: number
  description?: string
}

type GameState = {
  toneStats: ToneStats
  toneHistory: ToneHistoryEntry[]
  unlockedGlyphs: Set<string>
  accessibleEndings: string[]
  showDevConsole: boolean
  toggleDevConsole: () => void
  updateToneStats: (deltas: Partial<ToneStats>, description?: string) => void
  unlockGlyph: (glyphId: string) => void
  setAccessibleEndings: (endings: string[]) => void
}

const DEFAULT_TONE: ToneStats = {
  trust: 50,
  observation: 50,
  narrativePresence: 50,
  empathy: 50,
}

export const useGameStore = create<GameState>()(
  devtools((set, get) => ({
    toneStats: DEFAULT_TONE,
    toneHistory: [],
    unlockedGlyphs: new Set<string>(),
    accessibleEndings: [],
    showDevConsole: false,

    toggleDevConsole: () => set((s) => ({ showDevConsole: !s.showDevConsole })),

    updateToneStats: (deltas: Partial<ToneStats>, description?: string) => {
      const prev = get().toneStats
      const next: ToneStats = {
        trust: Math.max(0, Math.min(100, prev.trust + (deltas.trust ?? 0))),
        observation: Math.max(0, Math.min(100, prev.observation + (deltas.observation ?? 0))),
        narrativePresence: Math.max(0, Math.min(100, prev.narrativePresence + (deltas.narrativePresence ?? 0))),
        empathy: Math.max(0, Math.min(100, prev.empathy + (deltas.empathy ?? 0))),
      }
      const entry: ToneHistoryEntry[] = [
        ...get().toneHistory,
        ...Object.entries(deltas).map(([k, v]) => ({ statName: k, delta: v as number, description })),
      ]
      set(() => ({ toneStats: next, toneHistory: entry }))
    },

    unlockGlyph: (glyphId: string) => {
      const s = get()
      const setCopy = new Set(s.unlockedGlyphs)
      setCopy.add(glyphId)
      set(() => ({ unlockedGlyphs: setCopy }))
    },

    setAccessibleEndings: (endings: string[]) => set(() => ({ accessibleEndings: endings })),
  }))
)

export type { ToneStats, ToneHistoryEntry }

export default useGameStore
