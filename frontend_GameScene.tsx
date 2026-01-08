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
    <div style={{ position: 'relative', width: '100%', aspectRatio: '16/9' }}>
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

      {/* Narration Box */}
      <div
        style={{
          position: 'absolute',
          top: '20px',
          left: '20px',
          right: '20px',
          maxWidth: '500px',
          background: 'rgba(18, 18, 18, 0.85)',
          backdropFilter: 'blur(8px)',
          padding: '16px 20px',
          borderRadius: '10px',
          borderLeft: '4px solid #3a6df0',
          color: '#e0e0e0',
          fontSize: '15px',
          lineHeight: '1.6',
          zIndex: 10,
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

      {/* Controls Overlay */}
      <div
        style={{
          position: 'absolute',
          left: '20px',
          right: '20px',
          bottom: '20px',
          background: 'rgba(18, 18, 18, 0.85)',
          backdropFilter: 'blur(8px)',
          padding: '16px 20px',
          borderRadius: '10px',
          borderTop: '2px solid #3a6df0',
          zIndex: 10,
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
        }}
      >
        {/* Choice Buttons */}
        <div
          style={{
            display: 'flex',
            gap: '12px',
            flexWrap: 'wrap',
            marginBottom: '12px',
          }}
        >
          {choices.map((choice, index) => (
            <button
              key={index}
              onClick={() => handleChoiceClick(index)}
              style={{
                padding: '10px 16px',
                border: 'none',
                borderRadius: '8px',
                background: selectedChoice === index ? '#2563eb' : '#3a6df0',
                color: 'white',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '500',
                transition: 'all 0.2s ease',
                boxShadow: `0 2px 8px ${
                  selectedChoice === index
                    ? 'rgba(58, 109, 240, 0.5)'
                    : 'rgba(58, 109, 240, 0.3)'
                }`,
              }}
              onMouseEnter={(e) => {
                if (selectedChoice !== index) {
                  (e.target as HTMLButtonElement).style.background = '#2563eb';
                  (e.target as HTMLButtonElement).style.transform = 'translateY(-2px)';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedChoice !== index) {
                  (e.target as HTMLButtonElement).style.background = '#3a6df0';
                  (e.target as HTMLButtonElement).style.transform = 'translateY(0)';
                }
              }}
            >
              {choice.text}
            </button>
          ))}
        </div>

        {/* Custom Input */}
        <div
          style={{
            display: 'flex',
            gap: '8px',
            alignItems: 'center',
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
              minWidth: '200px',
              padding: '10px 12px',
              border: '1px solid #444',
              borderRadius: '8px',
              background: '#191b1e',
              color: '#e0e0e0',
              fontSize: '13px',
              fontFamily: 'inherit',
            }}
          />
          <button
            onClick={handleCustomSubmit}
            style={{
              padding: '10px 16px',
              border: 'none',
              borderRadius: '8px',
              background: '#4aa96c',
              color: 'white',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500',
              transition: 'all 0.2s ease',
              boxShadow: '0 2px 8px rgba(74, 169, 108, 0.3)',
            }}
            onMouseEnter={(e) => {
              (e.target as HTMLButtonElement).style.background = '#389e59';
              (e.target as HTMLButtonElement).style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              (e.target as HTMLButtonElement).style.background = '#4aa96c';
              (e.target as HTMLButtonElement).style.transform = 'translateY(0)';
            }}
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  );
}
