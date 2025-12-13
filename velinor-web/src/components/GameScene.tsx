// components/GameScene.tsx - Main game scene renderer with overlays

'use client';

import React, { useState } from 'react';
import Image from 'next/image';

interface GameSceneProps {
  backgroundImage: string;
  overlay?: string;
  narration: string;
  npcName?: string;
  choices: Array<{
    text: string;
    id?: string;
  }>;
  onChoiceClick: (choiceIndex: number) => void;
  onCustomInput?: (text: string) => void;
}

export default function GameScene({
  backgroundImage,
  overlay,
  narration,
  npcName = 'Scene',
  choices,
  onChoiceClick,
  onCustomInput,
}: GameSceneProps) {
  const [customInput, setCustomInput] = useState('');
  const [selectedChoice, setSelectedChoice] = useState<number | null>(null);

  const handleChoiceClick = (index: number) => {
    setSelectedChoice(index);
    onChoiceClick(index);
  };

  const handleCustomSubmit = () => {
    if (customInput.trim()) {
      onCustomInput?.(customInput);
      setCustomInput('');
    }
  };

  return (
    <div style={{ position: 'relative', width: '100%', maxWidth: '1200px', margin: '0 auto', aspectRatio: '16/9' }}>
      {/* Background Image */}
      <img
        src={backgroundImage}
        alt="Scene background"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          zIndex: 1,
        }}
      />

      {/* Overlay (dust, fog, etc.) */}
      {overlay && (
        <img
          src={overlay}
          alt="Scene overlay"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            opacity: 0.25,
            zIndex: 2,
          }}
        />
      )}

      {/* Narration Box - Top Left */}
      <div
        style={{
          position: 'absolute',
          top: '20px',
          left: '20px',
          maxWidth: '500px',
          background: 'rgba(18, 18, 18, 0.85)',
          backdropFilter: 'blur(8px)',
          padding: '16px 20px',
          borderRadius: '10px',
          borderLeft: '4px solid #3a6df0',
          color: '#e0e0e0',
          fontSize: '15px',
          lineHeight: '1.6',
          zIndex: 20,
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
        }}
      >
        <div
          style={{
            fontWeight: 'bold',
            color: '#64b5f6',
            marginBottom: '8px',
            fontSize: '13px',
            textTransform: 'uppercase',
            letterSpacing: '1px',
          }}
        >
          {npcName}
        </div>
        <div>{narration}</div>
      </div>

      {/* Choice Buttons - Overlaid on Image, Higher Up */}
      <div
        style={{
          position: 'absolute',
          bottom: '120px',
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: '12px',
          flexWrap: 'wrap',
          justifyContent: 'center',
          maxWidth: '90%',
          zIndex: 20,
        }}
      >
        {choices.map((choice, index) => (
          <button
            key={index}
            onClick={() => handleChoiceClick(index)}
            style={{
              padding: '12px 20px',
              border: '2px solid rgba(58, 109, 240, 0.8)',
              borderRadius: '8px',
              background:
                selectedChoice === index
                  ? 'rgba(37, 99, 235, 0.9)'
                  : 'rgba(58, 109, 240, 0.7)',
              color: 'white',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              transition: 'all 0.3s ease',
              boxShadow: `0 4px 15px ${
                selectedChoice === index
                  ? 'rgba(58, 109, 240, 0.6)'
                  : 'rgba(58, 109, 240, 0.4)'
              }`,
              backdropFilter: 'blur(4px)',
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.8)',
            }}
            onMouseEnter={(e) => {
              if (selectedChoice !== index) {
                (e.target as HTMLButtonElement).style.background =
                  'rgba(37, 99, 235, 0.95)';
                (e.target as HTMLButtonElement).style.transform =
                  'translateY(-4px) scale(1.05)';
                (e.target as HTMLButtonElement).style.boxShadow =
                  '0 6px 20px rgba(58, 109, 240, 0.7)';
              }
            }}
            onMouseLeave={(e) => {
              if (selectedChoice !== index) {
                (e.target as HTMLButtonElement).style.background =
                  'rgba(58, 109, 240, 0.7)';
                (e.target as HTMLButtonElement).style.transform =
                  'translateY(0) scale(1)';
                (e.target as HTMLButtonElement).style.boxShadow =
                  '0 4px 15px rgba(58, 109, 240, 0.4)';
              }
            }}
          >
            {choice.text}
          </button>
        ))}
      </div>

      {/* Custom Input - Bottom */}
      <div
        style={{
          position: 'absolute',
          bottom: '10px',
          left: '20px',
          right: '20px',
          display: 'flex',
          gap: '8px',
          alignItems: 'center',
          maxWidth: '600px',
          zIndex: 20,
        }}
      >
        <input
          type="text"
          value={customInput}
          onChange={(e) => setCustomInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleCustomSubmit()}
          placeholder="Type a custom action..."
          style={{
            flex: 1,
            minWidth: '150px',
            padding: '10px 12px',
            border: '1px solid rgba(68, 68, 68, 0.8)',
            borderRadius: '8px',
            background: 'rgba(25, 27, 30, 0.85)',
            color: '#e0e0e0',
            fontSize: '13px',
            fontFamily: 'inherit',
            backdropFilter: 'blur(4px)',
          }}
        />
        <button
          onClick={handleCustomSubmit}
          style={{
            padding: '10px 16px',
            border: '2px solid rgba(74, 169, 108, 0.8)',
            borderRadius: '8px',
            background: 'rgba(74, 169, 108, 0.8)',
            color: 'white',
            cursor: 'pointer',
            fontSize: '13px',
            fontWeight: '600',
            transition: 'all 0.2s ease',
            boxShadow: '0 2px 8px rgba(74, 169, 108, 0.4)',
            backdropFilter: 'blur(4px)',
          }}
          onMouseEnter={(e) => {
            (e.target as HTMLButtonElement).style.background =
              'rgba(56, 158, 89, 0.95)';
            (e.target as HTMLButtonElement).style.transform = 'translateY(-2px)';
          }}
          onMouseLeave={(e) => {
            (e.target as HTMLButtonElement).style.background =
              'rgba(74, 169, 108, 0.8)';
            (e.target as HTMLButtonElement).style.transform = 'translateY(0)';
          }}
        >
          Submit
        </button>
      </div>
    </div>
  );
}
