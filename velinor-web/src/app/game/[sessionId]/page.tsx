'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import GameScene from '@/components/GameScene';
import scenesData from '@/data/scenes.json';

export default function GamePage() {
  const router = useRouter();
  const params = useParams();
  const [currentSceneId, setCurrentSceneId] = useState<string>('velhara_market');
  const [gameState, setGameState] = useState<any>(null);

  // Load scene from JSON data
  useEffect(() => {
    const sceneId = params.sessionId as string;
    if (sceneId) {
      setCurrentSceneId(sceneId);
    }
  }, [params.sessionId]);

  // Get current scene from data
  useEffect(() => {
    const scene = scenesData.find((s: any) => s.id === currentSceneId);
    if (scene) {
      setGameState(scene);
    }
  }, [currentSceneId]);

  const handleChoiceClick = (choiceIndex: number) => {
    if (gameState?.choices && gameState.choices[choiceIndex]) {
      const nextSceneId = gameState.choices[choiceIndex].next;
      router.push(`/game/${nextSceneId}`);
    }
  };

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
        Loading scene...
      </div>
    );
  }

  return (
    <div style={{ 
      width: '100%', 
      minHeight: '100vh',
      padding: '20px', 
      background: '#000' 
    }}>
      <GameScene
        backgroundImage={gameState.background}
        narration={gameState.text}
        npcName={gameState.npc_name || gameState.id}
        choices={gameState.choices || []}
        onChoiceClick={handleChoiceClick}
      />
    </div>
  );
}
