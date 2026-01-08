/**
 * ToneStatsDisplay Component - Dev console for monitoring TONE stats
 * Shows real-time TONE stat changes and accessible game content
 */

'use client';

import React from 'react';
import { useGameStore } from '@/lib/gameStore';
import {
    formatToneStats,
    getToneTier,
    getUnlockableGlyphs,
    getAccessibleEndings,
} from '@/lib/toneSystem';

export default function ToneStatsDisplay() {
    const {
        toneStats,
        toneHistory,
        unlockedGlyphs,
        accessibleEndings,
        showDevConsole,
        toggleDevConsole,
    } = useGameStore();

    const formattedStats = formatToneStats(toneStats);
    const currentUnlockableGlyphs = getUnlockableGlyphs(toneStats);

    if (!showDevConsole) {
        return (
            <button
                onClick={toggleDevConsole}
                style={{
                    position: 'fixed',
                    bottom: '20px',
                    right: '20px',
                    padding: '10px 16px',
                    fontSize: '12px',
                    background: 'rgba(58, 109, 240, 0.6)',
                    border: '1px solid rgba(58, 109, 240, 0.8)',
                    color: '#e0e0e0',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    zIndex: 100,
                }}
            >
                Dev Console
            </button>
        );
    }

    return (
        <div
            style={{
                position: 'fixed',
                bottom: '20px',
                right: '20px',
                width: '350px',
                maxHeight: '600px',
                background: 'rgba(18, 18, 18, 0.95)',
                border: '2px solid rgba(58, 109, 240, 0.8)',
                borderRadius: '8px',
                padding: '16px',
                color: '#e0e0e0',
                fontSize: '12px',
                overflowY: 'auto',
                zIndex: 101,
                fontFamily: 'monospace',
            }}
        >
            {/* Header */}
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '12px',
                    paddingBottom: '8px',
                    borderBottom: '1px solid rgba(58, 109, 240, 0.5)',
                }}
            >
                <div style={{ color: '#64b5f6', fontWeight: 'bold' }}>TONE SYSTEM</div>
                <button
                    onClick={toggleDevConsole}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: '#e0e0e0',
                        cursor: 'pointer',
                        fontSize: '14px',
                        padding: 0,
                    }}
                >
                    ✕
                </button>
            </div>

            {/* Current Stats */}
            <div style={{ marginBottom: '12px' }}>
                <div style={{ color: '#64b5f6', marginBottom: '6px', fontWeight: 'bold' }}>
                    Current Stats
                </div>
                <div style={{ lineHeight: '1.6' }}>
                    <div>
                        Trust:{' '}
                        <span style={{ color: getToneValueColor(toneStats.trust) }}>
                            {formattedStats.trust} ({getToneTier(toneStats.trust)})
                        </span>
                    </div>
                    <div>
                        Observation:{' '}
                        <span style={{ color: getToneValueColor(toneStats.observation) }}>
                            {formattedStats.observation} ({getToneTier(toneStats.observation)})
                        </span>
                    </div>
                    <div>
                        Narrative Presence:{' '}
                        <span style={{ color: getToneValueColor(toneStats.narrativePresence) }}>
                            {formattedStats.narrativePresence} ({getToneTier(toneStats.narrativePresence)})
                        </span>
                    </div>
                    <div>
                        Empathy:{' '}
                        <span style={{ color: getToneValueColor(toneStats.empathy) }}>
                            {formattedStats.empathy} ({getToneTier(toneStats.empathy)})
                        </span>
                    </div>
                </div>
            </div>

            {/* Unlocked Glyphs */}
            <div style={{ marginBottom: '12px' }}>
                <div style={{ color: '#64b5f6', marginBottom: '6px', fontWeight: 'bold' }}>
                    Unlocked Glyphs ({unlockedGlyphs.size})
                </div>
                {unlockedGlyphs.size > 0 ? (
                    <div style={{ lineHeight: '1.4', fontSize: '11px' }}>
                        {Array.from(unlockedGlyphs).map(glyph => (
                            <div key={glyph} style={{ color: '#81c784' }}>
                                ✓ {glyph}
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{ color: '#999', fontSize: '11px' }}>No glyphs unlocked yet</div>
                )}
            </div>

            {/* Unlockable Glyphs */}
            {currentUnlockableGlyphs.length > unlockedGlyphs.size && (
                <div style={{ marginBottom: '12px' }}>
                    <div style={{ color: '#fbc02d', marginBottom: '6px', fontWeight: 'bold' }}>
                        Nearly Unlocked
                    </div>
                    <div style={{ lineHeight: '1.4', fontSize: '11px' }}>
                        {currentUnlockableGlyphs
                            .filter(g => !unlockedGlyphs.has(g))
                            .map(glyph => (
                                <div key={glyph} style={{ color: '#fbc02d' }}>
                                    ◐ {glyph}
                                </div>
                            ))}
                    </div>
                </div>
            )}

            {/* Accessible Endings */}
            <div style={{ marginBottom: '12px' }}>
                <div style={{ color: '#64b5f6', marginBottom: '6px', fontWeight: 'bold' }}>
                    Accessible Endings ({accessibleEndings.length})
                </div>
                {accessibleEndings.length > 0 ? (
                    <div style={{ lineHeight: '1.4', fontSize: '11px' }}>
                        {accessibleEndings.map(ending => (
                            <div key={ending} style={{ color: '#ce93d8' }}>
                                ► {ending}
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{ color: '#999', fontSize: '11px' }}>Continue playing to unlock endings</div>
                )}
            </div>

            {/* Recent History */}
            {toneHistory.length > 0 && (
                <div>
                    <div style={{ color: '#64b5f6', marginBottom: '6px', fontWeight: 'bold' }}>
                        Recent Changes
                    </div>
                    <div style={{ lineHeight: '1.3', fontSize: '10px', maxHeight: '100px', overflowY: 'auto' }}>
                        {toneHistory.slice(-5).map((action, idx) => (
                            <div key={idx} style={{ color: '#90caf9', marginBottom: '4px' }}>
                                {action.statName}: {action.delta > 0 ? '+' : ''}{action.delta}
                                {action.description && ` (${action.description})`}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

function getToneValueColor(value: number): string {
    if (value < 30) return '#f44336'; // Red
    if (value < 50) return '#ff9800'; // Orange
    if (value < 70) return '#fbc02d'; // Yellow
    if (value < 85) return '#81c784'; // Light green
    return '#4caf50'; // Green
}
