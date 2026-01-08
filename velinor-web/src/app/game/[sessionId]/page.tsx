'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams, useSearchParams } from 'next/navigation';
import GameScene from '@/components/GameScene';
import dynamic from 'next/dynamic';
// Load KaeleScene dynamically (client-only)
const KaeleScene = dynamic(() => import('@/components/KaeleScene'), { ssr: false });
import ToneStatsDisplay from '@/components/ToneStatsDisplay';
import { useGameStore } from '@/lib/gameStore';
import { gameApi } from '@/lib/api';

interface GameState {
  session_id: string;
  passage_id: string;
  passage_name: string;
  main_dialogue: string;
  npc_name?: string;
  npc_dialogue?: string;
  background_image?: string;
  choices: Array<{
    index: number;
    text: string;
  }>;
  has_clarifying_question: boolean;
  clarifying_question?: string;
  game_state?: Record<string, any>;
}

export default function GamePage() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Initialize game session
  useEffect(() => {
    const initGame = async () => {
      try {
        const playerName = searchParams.get('player') || 'Traveler';

        // Start a new game session via backend API
        const data = await gameApi.startGame(playerName);
        setSessionId(data.session_id);
        setGameState(data);
        setLoading(false);
      } catch (err) {
        setError(`Failed to initialize game: ${err}`);
        setLoading(false);
      }
    };

    initGame();
  }, [searchParams]);

  const handleChoiceClick = async (choiceIndex: number) => {
    if (!sessionId) return;

    try {
      const data = await gameApi.takeAction(choiceIndex, undefined, sessionId);
      setGameState(data);
    } catch (err) {
      setError(`Action failed: ${err}`);
    }
  };

  if (loading) {
    return (
      <div style={{
        width: '100%',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#000',
        color: '#fff',
        fontSize: '1.2rem',
      }}>
        Initializing game...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        width: '100%',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#000',
        color: '#ff6b6b',
        fontSize: '1.2rem',
        padding: '20px',
        textAlign: 'center',
      }}>
        <div>
          <h2>Error</h2>
          <p>{error}</p>
          <button
            onClick={() => router.push('/')}
            style={{
              marginTop: '20px',
              padding: '10px 24px',
              background: '#2e3f2f',
              color: '#e6d8b4',
              border: '1px solid #a88f5c',
              borderRadius: '8px',
              cursor: 'pointer',
              fontFamily: 'serif',
              fontSize: '1rem',
              letterSpacing: '0.5px',
              boxShadow: '0 0 8px rgba(168, 143, 92, 0.3)',
              transition: 'all 0.3s ease',
            }}
            onMouseOver={(e) => {
              (e.target as HTMLButtonElement).style.background = '#3b4f3b';
              (e.target as HTMLButtonElement).style.boxShadow = '0 0 12px rgba(168, 143, 92, 0.5)';
            }}
            onMouseOut={(e) => {
              (e.target as HTMLButtonElement).style.background = '#2e3f2f';
              (e.target as HTMLButtonElement).style.boxShadow = '0 0 8px rgba(168, 143, 92, 0.3)';
            }}
          >
            Return to Menu
          </button>
        </div>
      </div>
    );
  }

  if (!gameState) {
    return (
      <div style={{
        width: '100%',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#000',
        color: '#fff',
        fontSize: '1.2rem',
      }}>
        Loading game state...
      </div>
    );
  }

  // Determine whether to render KaeleScene for Kaelen/trickster encounters
  const npcNameLower = (gameState.npc_name || '').toLowerCase();
  const passageLower = (gameState.passage_name || '').toLowerCase();

  // Derive player stats and possible glyphs
  const playerStats = gameState.game_state?.player_stats || {};
  const glyphs = gameState.game_state?.glyphs_collected || gameState.game_state?.player_stats?.glyphs_collected || [];
  const hasStillness = Array.isArray(glyphs) ? glyphs.includes('Stillness') : !!glyphs;

  // Persona selection heuristic:
  // - If NPC name explicitly contains "kaelen" or "trickster", use that persona
  // - If we're in the swamp passage, prefer trickster for low empathy, Kaelen for higher empathy
  let persona: 'kaelen' | 'trickster' = 'kaelen';
  if (npcNameLower.includes('trickster')) persona = 'trickster';
  else if (npcNameLower.includes('kaelen')) persona = 'kaelen';
  else if (passageLower.includes('swamp') || (gameState.scene_id === 'swamp_scene')) {
    const empathy = typeof playerStats.empathy === 'number' ? playerStats.empathy : 0;
    persona = empathy < 50 ? 'trickster' : 'kaelen';
  }

  return (
    <div style={{
      width: '100%',
      minHeight: '100vh',
      padding: '20px',
      background: '#000'
    }}>
      {((npcNameLower.includes('kaelen') || npcNameLower.includes('trickster') || gameState.scene_id === 'swamp_scene')) ? (
        <KaeleScene
          scenarioType={gameState.scene_id === 'swamp_scene' ? 'swamp' : 'marketplace'}
          autoAlternate={gameState.scene_id === 'swamp_scene'}
          alternateInterval={2000}
          persona={persona}
          playerHasStillness={hasStillness}
        />
      ) : (
        <GameScene
          backgroundImage={gameState.background_image || '/assets/backgrounds/velhara_market.png'}
          narration={gameState.main_dialogue}
          npcName={gameState.npc_name || gameState.passage_name}
          choices={gameState.choices.map((c, i) => ({ text: c.text, id: i.toString() }))}
          onChoiceClick={handleChoiceClick}
        />
      )}

      {/* TONE Stats Display Dev Console */}
      <ToneStatsDisplay />

      {/* Debug info - shows variable count */}
      {gameState.game_state && (
        <div style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          background: 'rgba(0, 0, 0, 0.8)',
          color: '#64b5f6',
          padding: '10px 15px',
          borderRadius: '8px',
          fontSize: '12px',
          zIndex: 30,
        }}>
          Variables: {Object.keys(gameState.game_state).length}
        </div>
      )}
    </div>
  );
}

