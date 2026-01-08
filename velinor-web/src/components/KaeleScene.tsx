'use client';

import React, { useState, useEffect } from 'react';

interface KaeleSceneProps {
  onDialogueChange?: (lineIndex: number) => void;
  scenarioType?: 'marketplace' | 'swamp' | 'confrontation';
  autoAlternate?: boolean;
  alternateInterval?: number;
  persona?: 'kaelen' | 'trickster';
  playerHasStillness?: boolean;
}

const KAELEN_DIALOGUES = {
  marketplace: [
    "Eyes forward. Most people don't see me. You do. That's either good or bad.",
    "What brings you to the marketplace, stranger? Looking for something... or someone?",
    "I hear things. I see things. And I remember things others forget.",
    "Trust is a commodity here. More valuable than coin.",
    "Be careful who you tell your secrets to. They have a way of traveling.",
  ],
  swamp: [
    "This place… it's not what he said it was. Feels like the swamp's playin' tricks.",
    "The quiet ones are the dangerous ones. Not because they're loud, but because they know how to wait.",
    "You're holdin' his secrets now. Don't carry them lightly.",
    "Follow close. The swamp doesn't trust easy passages.",
    "Each token tells a story. Together, they're a voice.",
  ],
  confrontation: [
    "So... you came. I wasn't sure you would.",
    "Drossel taught me many things. Not all of them were kind.",
    "You found the tokens. Then you know what I know.",
    "There are choices here. Some of them fracture trust.",
    "Whatever happens next... remember this moment.",
  ]
};

// Trickster voice: smoother, deliberate, unconcerned with hurry
const TRICKSTER_DIALOGUES = {
  marketplace: [
    "Ah—wanderer. Markets keep their secrets if you know how to ask.",
    "Do you look for wares or for memory? Sometimes they're the same.",
    "Stories here fold over themselves. Best to hold a lantern, not a ledger.",
    "Patience, friend. The bargains that matter are never shouted.",
    "Names are soft things. Say one too loud and it slips away."
  ],
  swamp: [
    "This fog keeps its own counsel. Step slow; the land remembers badly.",
    "Stone and water whisper different histories. I prefer the quieter ones.",
    "You'll find the paths if you listen to where the mud pays attention.",
    "Stillness is a choice. Some choose badly. Some choose to forget.",
    "Enjoy the confusion; it makes the pieces look new again."
  ],
  confrontation: [
    "You arrive. Timings are curious these days.",
    "Fragments suit me—broken lines make for better conversation.",
    "When memory loosens, people become interesting again.",
    "I will not rush you. The world will do that for us both.",
    "When someone asks, say nothing. That is often the answer."
  ]
};

/**
 * KaeleScene Component
 * 
 * Renders Kaelen with alternating forward/side poses to create a shifty, unpredictable effect.
 * The images alternate based on dialogue changes or auto-timing.
 * 
 * Usage:
 * ```tsx
 * <KaeleScene 
 *   scenarioType="marketplace"
 *   autoAlternate={true}
 *   alternateInterval={2000}
 * />
 * ```
 */
export default function KaeleScene({
  onDialogueChange,
  scenarioType = 'marketplace',
  autoAlternate = false,
  alternateInterval = 2000,
  persona = 'kaelen',
  playerHasStillness = false,
}: KaeleSceneProps) {
  const [dialogueIndex, setDialogueIndex] = useState(0);
  const [imageIndex, setImageIndex] = useState(0); // 0 = forward, 1 = side
  const [isAnimating, setIsAnimating] = useState(false);

  // Select dialogue bank based on persona
  const dialogues = persona === 'trickster' ? TRICKSTER_DIALOGUES[scenarioType] : KAELEN_DIALOGUES[scenarioType];
  const currentDialogue = dialogues[dialogueIndex % dialogues.length];

  // Image URLs - using placeholder paths for the user's provided images
  // These should be updated to actual paths when images are uploaded
  const kaeleForwardUrl = '/velinor/npcs/kaelen_forward.png';
  const kaeleSideUrl = '/velinor/npcs/kaelen_side.png';
  const currentImageUrl = imageIndex === 0 ? kaeleForwardUrl : kaeleSideUrl;

  // Auto-alternate images based on timing
  useEffect(() => {
    if (!autoAlternate) return;

    const interval = setInterval(() => {
      setImageIndex(prev => {
        const newIndex = (prev + 1) % 2;
        setIsAnimating(true);
        setTimeout(() => setIsAnimating(false), 300);
        return newIndex;
      });
    }, alternateInterval);

    return () => clearInterval(interval);
  }, [autoAlternate, alternateInterval]);

  const handleNextDialogue = () => {
    // Alternate image with each dialogue change
    setImageIndex(prev => (prev + 1) % 2);
    setIsAnimating(true);
    setTimeout(() => setIsAnimating(false), 300);

    setDialogueIndex(prev => prev + 1);
    onDialogueChange?.(dialogueIndex + 1);
  };

  const handlePreviousDialogue = () => {
    if (dialogueIndex > 0) {
      setImageIndex(prev => (prev + 1) % 2);
      setIsAnimating(true);
      setTimeout(() => setIsAnimating(false), 300);

      setDialogueIndex(prev => prev - 1);
      onDialogueChange?.(dialogueIndex - 1);
    }
  };

  const containerStyle: React.CSSProperties = {
    position: 'relative',
    width: '100%',
    maxWidth: '1000px',
    margin: '0 auto',
    padding: '40px 20px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '24px',
    background: 'linear-gradient(135deg, rgba(25, 27, 30, 0.95) 0%, rgba(20, 22, 26, 0.95) 100%)',
    borderRadius: '16px',
    border: '1px solid rgba(168, 143, 92, 0.3)',
    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.7)',
  };

  const imageContainerStyle: React.CSSProperties = {
    position: 'relative',
    width: '280px',
    height: '360px',
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'center',
    background: 'radial-gradient(ellipse at center bottom, rgba(168, 143, 92, 0.1) 0%, transparent 70%)',
    borderRadius: '12px',
    overflow: 'hidden',
    border: '1px solid rgba(168, 143, 92, 0.2)',
  };

  const imageStyle: React.CSSProperties = {
    width: '100%',
    height: '100%',
    objectFit: 'contain',
    opacity: isAnimating ? 0.7 : 1,
    transition: 'opacity 0.3s ease, transform 0.3s ease',
    transform: isAnimating ? 'scale(0.98)' : 'scale(1)',
  };

  const dialogueBoxStyle: React.CSSProperties = {
    width: '100%',
    padding: '24px',
    minHeight: '120px',
    background: 'rgba(0, 0, 0, 0.5)',
    border: '1px solid rgba(168, 143, 92, 0.3)',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  };

  const dialogueTextStyle: React.CSSProperties = {
    color: '#e6d8b4',
    fontSize: '1.1rem',
    fontFamily: 'Georgia, serif',
    fontStyle: 'italic',
    textAlign: 'center',
    lineHeight: '1.6',
    textShadow: '0 2px 4px rgba(0, 0, 0, 0.8)',
    margin: 0,
  };

  const buttonsContainerStyle: React.CSSProperties = {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
    width: '100%',
  };

  const buttonStyle: React.CSSProperties = {
    padding: '10px 20px',
    fontSize: '0.95rem',
    fontFamily: 'Georgia, serif',
    fontWeight: 'bold',
    background: 'linear-gradient(135deg, #2e3f2f 0%, #1a2219 100%)',
    color: '#e6d8b4',
    border: '1px solid #a88f5c',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.5)',
  };

  const buttonHoverStyle: React.CSSProperties = {
    ...buttonStyle,
    background: 'linear-gradient(135deg, #3b4f3b 0%, #254d25 100%)',
    boxShadow: '0 4px 12px rgba(168, 143, 92, 0.3)',
    transform: 'translateY(-2px)',
  };

  const indicatorStyle: React.CSSProperties = {
    color: '#a88f5c',
    fontSize: '0.9rem',
    textAlign: 'center',
    fontStyle: 'italic',
  };

  return (
    <div style={containerStyle}>
      <div style={imageContainerStyle}>
        <img
          src={currentImageUrl}
          alt="Kaelen"
          style={imageStyle}
          onError={(e) => {
            // Fallback if image doesn't exist
            const target = e.target as HTMLImageElement;
            target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="280" height="360"%3E%3Crect fill="%23333" width="280" height="360"/%3E%3Ctext x="50%25" y="50%25" font-family="serif" font-size="16" fill="%23999" text-anchor="middle" dominant-baseline="middle"%3EKaelen Image%3C/text%3E%3C/svg%3E';
          }}
        />
      </div>

      <div style={dialogueBoxStyle}>
        {/* If player has Stillness, Kaelen (not trickster) offers a small clarifying line */}
        {playerHasStillness && persona === 'kaelen' ? (
          <p style={dialogueTextStyle}>"{currentDialogue} {`\n`}—You hold stillness. It steadies the path."</p>
        ) : (
          <p style={dialogueTextStyle}>"{currentDialogue}"</p>
        )}
      </div>

      <div style={buttonsContainerStyle}>
        <button
          onClick={handlePreviousDialogue}
          style={buttonStyle}
          disabled={dialogueIndex === 0}
          onMouseEnter={(e) => {
            if (dialogueIndex > 0) {
              const target = e.currentTarget as HTMLButtonElement;
              Object.assign(target.style, buttonHoverStyle);
            }
          }}
          onMouseLeave={(e) => {
            const target = e.currentTarget as HTMLButtonElement;
            Object.assign(target.style, buttonStyle);
            if (dialogueIndex === 0) {
              target.style.opacity = '0.5';
              target.style.cursor = 'not-allowed';
            }
          }}
        >
          ← Previous
        </button>

        <button
          onClick={handleNextDialogue}
          style={buttonStyle}
          onMouseEnter={(e) => {
            const target = e.currentTarget as HTMLButtonElement;
            Object.assign(target.style, buttonHoverStyle);
          }}
          onMouseLeave={(e) => {
            const target = e.currentTarget as HTMLButtonElement;
            Object.assign(target.style, buttonStyle);
          }}
        >
          Next →
        </button>
      </div>

      <div style={indicatorStyle}>
        Line {dialogueIndex + 1} of {dialogues.length}
        <br />
        <span style={{ fontSize: '0.85rem', color: '#8b7d6b' }}>
          {imageIndex === 0 ? '↔ Facing Forward' : '↔ Looking Aside'}
        </span>
      </div>
    </div>
  );
}
