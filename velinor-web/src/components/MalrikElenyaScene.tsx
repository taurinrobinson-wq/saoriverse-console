"use client";

import React, { useEffect, useState } from 'react';
import createSnapshot from '../../../velinor/game_mechanics/frontend_api';
import data from '../../../velinor/markdowngameinstructions/malrik_elenya_coren.json';

const ORIENTATIONS = ['trust', 'observation', 'narrative', 'empathy'] as const;

export default function MalrikElenyaScene() {
    const [snap] = useState(() => createSnapshot.createToneSnapshot());
    const [orientation, setOrientation] = useState<string>('empathy');
    const [state, setState] = useState(() => ({ tone: snap.tone, attunement: snap.attunement, correlation: snap.correlation }));

    useEffect(() => {
        setState({ tone: snap.tone, attunement: snap.attunement, correlation: snap.correlation });
    }, [snap]);

    const choiceSets = data.miniGames.observationalScene.choiceSets;

    function applyChoice(index: number) {
        const res = snap.applyChoice(orientation, index);
        setState({ tone: res.tone, attunement: res.attunement, correlation: res.correlation });
    }

    return (
        <div style={{ color: '#e6d8b4', padding: 24, fontFamily: 'Georgia, serif' }}>
            <h2>Malrik & Elenya — Observational Scene</h2>
            <p style={{ color: '#a88f5c' }}>Use the dropdown to pick an orientation and choose how the player interprets the scene.</p>

            <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginTop: 12 }}>
                <label style={{ color: '#e6d8b4' }}>Orientation:</label>
                <select value={orientation} onChange={(e) => setOrientation(e.target.value)} style={{ padding: 8, borderRadius: 6 }}>
                    {ORIENTATIONS.map(o => <option key={o} value={o}>{o}</option>)}
                </select>
            </div>

            <div style={{ marginTop: 20 }}>
                <strong>Choices ({orientation}):</strong>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
                    {choiceSets[orientation].map((c: string, i: number) => (
                        <button key={i} onClick={() => applyChoice(i)} style={{ padding: '10px 12px', borderRadius: 8, background: '#2e3f2f', color: '#e6d8b4', border: '1px solid #a88f5c', textAlign: 'left' }}>
                            {c}
                        </button>
                    ))}
                </div>
            </div>

            <div style={{ marginTop: 20 }}>
                <strong>Tone State</strong>
                <pre style={{ background: 'rgba(20,20,20,0.6)', padding: 12, borderRadius: 8 }}>{JSON.stringify(state.tone, null, 2)}</pre>
                <p>Attunement: {state.attunement.toFixed(3)}</p>
                <p>Malrik/Elenya correlation: {state.correlation}</p>
            </div>

            <div style={{ marginTop: 24 }}>
                <button onClick={() => window.location.reload()} style={{ padding: '10px 14px', borderRadius: 8, background: '#3b4f3b', color: '#e6d8b4' }}>Reset Scene</button>
            </div>
        </div>
    );
}
