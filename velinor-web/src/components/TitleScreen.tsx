'use client';

import { useState, CSSProperties } from 'react';
import { useRouter } from 'next/navigation';

interface TitleScreenProps {
  onGameStart?: (playerName: string) => void;
}

export default function TitleScreen({ onGameStart }: TitleScreenProps) {
  const router = useRouter();
  const [playerName, setPlayerName] = useState('');
  const [showNameInput, setShowNameInput] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleStartButtonClick = () => {
    setShowNameInput(true);
    setError('');
  };

  const handleConfirmName = async () => {
    if (!playerName.trim()) {
      setError('Please enter a character name');
      return;
    }

    setLoading(true);
    setError('');
    try {
      if (onGameStart) {
        onGameStart(playerName);
      } else {
        router.push(`/game/velhara_market?player=${encodeURIComponent(playerName)}`);
      }
    } catch (err) {
      console.error('Failed to start game:', err);
      setError('Failed to start game');
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setShowNameInput(false);
    setPlayerName('');
    setError('');
  };

  const containerStyle: CSSProperties = {
    position: 'relative',
    width: '100%',
    height: '100vh',
    overflow: 'hidden',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  };

  // Layer 1: Background with blur
  const backgroundStyle: CSSProperties = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    zIndex: 1,
    filter: 'blur(2px)',
  };

  // Layer 2: Velinor character overlay
  const velinorStyle: CSSProperties = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '100%',
    height: '100%',
    maxWidth: '1200px',
    maxHeight: '800px',
    objectFit: 'contain',
    zIndex: 2,
    opacity: 0.95,
  };

  // Layer 3: Title overlay
  const titleOverlayStyle: CSSProperties = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '16.5%',
    height: 'auto',
    objectFit: 'contain',
    zIndex: 3,
    pointerEvents: 'none',
  };

  // Layer 4: Button overlay
  const buttonStyle: CSSProperties = {
    position: 'absolute',
    bottom: '120px',
    left: '50%',
    transform: 'translateX(-50%)',
    padding: '14px 40px',
    fontSize: '1.1rem',
    fontWeight: 'bold',
    background: 'linear-gradient(135deg, #2e3f2f 0%, #1a2219 100%)',
    color: '#e6d8b4',
    border: '2px solid #a88f5c',
    borderRadius: '12px',
    cursor: 'pointer',
    zIndex: 10,
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    boxShadow: '0 4px 12px rgba(168, 143, 92, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(4px)',
    textShadow: '0 2px 4px rgba(0, 0, 0, 0.8)',
    fontFamily: 'Georgia, serif',
    letterSpacing: '1px',
    textTransform: 'uppercase',
    whiteSpace: 'nowrap',
    outline: 'none',
  };

  const buttonHoverStyle: CSSProperties = {
    ...buttonStyle,
    background: 'linear-gradient(135deg, #3b4f3b 0%, #254d25 100%)',
    boxShadow: '0 6px 16px rgba(168, 143, 92, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15)',
    transform: 'translateX(-50%) translateY(-3px)',
  };

  const buttonActiveStyle: CSSProperties = {
    ...buttonStyle,
    background: 'linear-gradient(135deg, #1a2819 0%, #0f1a0f 100%)',
    boxShadow: '0 2px 8px rgba(168, 143, 92, 0.2), inset 0 1px 2px rgba(0, 0, 0, 0.4)',
    transform: 'translateX(-50%) translateY(0)',
  };

  return (
    <main style={containerStyle}>
      {/* Layer 1: Background */}
      <img
        src="/assets/backgrounds/Velhara_background_title(blur).png"
        alt="Velhara Background"
        style={backgroundStyle}
      />

      {/* Layer 2: Velinor Character */}
      <img
        src="/assets/npcs/velinor_eyesclosed2.png"
        alt="Velinor"
        style={velinorStyle}
      />

      {/* Layer 3: Title Overlay */}
      <img
        src="/assets/overlays/velinor_title_transparent2.png"
        alt="Velinor Title"
        style={titleOverlayStyle}
      />

      {/* Layer 4: Play New Game Button */}
      <button
        onClick={handleStartButtonClick}
        style={buttonStyle}
        onMouseEnter={(e) => {
          const target = e.currentTarget as HTMLButtonElement;
          Object.assign(target.style, buttonHoverStyle);
        }}
        onMouseLeave={(e) => {
          const target = e.currentTarget as HTMLButtonElement;
          Object.assign(target.style, buttonStyle);
        }}
        onMouseDown={(e) => {
          const target = e.currentTarget as HTMLButtonElement;
          Object.assign(target.style, buttonActiveStyle);
        }}
        onMouseUp={(e) => {
          const target = e.currentTarget as HTMLButtonElement;
          Object.assign(target.style, buttonHoverStyle);
        }}
        onBlur={(e) => {
          const target = e.currentTarget as HTMLButtonElement;
          Object.assign(target.style, buttonStyle);
        }}
      >
        Play New Game
      </button>

      {/* Player Name Input Modal */}
      {showNameInput && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            backdropFilter: 'blur(8px)',
            animation: 'fadeIn 0.2s ease-in',
          }}
          onClick={handleCancel}
        >
          {/* Modal Content */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(25, 27, 30, 0.98) 0%, rgba(20, 22, 26, 0.98) 100%)',
              borderRadius: '16px',
              padding: '48px 40px',
              maxWidth: '420px',
              width: '90%',
              textAlign: 'center',
              border: '2px solid rgba(168, 143, 92, 0.6)',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.9), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(16px)',
              animation: 'slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2
              style={{
                color: '#e6d8b4',
                marginBottom: '12px',
                fontSize: '1.8rem',
                fontWeight: 'bold',
                fontFamily: 'Georgia, serif',
                letterSpacing: '1px',
              }}
            >
              Enter Your Name
            </h2>
            <p
              style={{
                color: '#a88f5c',
                marginBottom: '32px',
                fontSize: '0.95rem',
                fontStyle: 'italic',
              }}
            >
              Choose a name for your journey through Velhara
            </p>

            {/* Input Field */}
            <input
              type="text"
              value={playerName}
              onChange={(e) => {
                setPlayerName(e.target.value);
                setError('');
              }}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleConfirmName();
                }
              }}
              placeholder="Your character name"
              maxLength={30}
              style={{
                width: '100%',
                padding: '14px 16px',
                marginBottom: error ? '12px' : '28px',
                fontSize: '1rem',
                background: 'rgba(40, 45, 55, 0.6)',
                color: '#e6d8b4',
                border: '2px solid rgba(168, 143, 92, 0.4)',
                borderRadius: '8px',
                outline: 'none',
                transition: 'all 0.2s ease',
                fontFamily: 'serif',
                boxSizing: 'border-box',
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = 'rgba(168, 143, 92, 0.8)';
                e.currentTarget.style.boxShadow = '0 0 8px rgba(168, 143, 92, 0.3)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = 'rgba(168, 143, 92, 0.4)';
                e.currentTarget.style.boxShadow = 'none';
              }}
              autoFocus
            />

            {/* Error Message */}
            {error && (
              <p
                style={{
                  color: '#ff6b6b',
                  fontSize: '0.85rem',
                  marginBottom: '20px',
                  fontWeight: 'bold',
                }}
              >
                {error}
              </p>
            )}

            {/* Button Container */}
            <div
              style={{
                display: 'flex',
                gap: '12px',
                justifyContent: 'center',
              }}
            >
              {/* Confirm Button */}
              <button
                onClick={handleConfirmName}
                disabled={loading}
                style={{
                  flex: 1,
                  padding: '12px 24px',
                  fontSize: '1rem',
                  fontWeight: 'bold',
                  background: loading ? '#5a6b5a' : 'linear-gradient(135deg, #2e3f2f 0%, #1a2219 100%)',
                  color: '#e6d8b4',
                  border: '2px solid #a88f5c',
                  borderRadius: '8px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s ease',
                  fontFamily: 'serif',
                  letterSpacing: '0.5px',
                  opacity: loading ? 0.6 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    const target = e.currentTarget as HTMLButtonElement;
                    target.style.background = 'linear-gradient(135deg, #3b4f3b 0%, #254d25 100%)';
                    target.style.boxShadow = '0 4px 12px rgba(168, 143, 92, 0.4)';
                  }
                }}
                onMouseLeave={(e) => {
                  const target = e.currentTarget as HTMLButtonElement;
                  target.style.background = 'linear-gradient(135deg, #2e3f2f 0%, #1a2219 100%)';
                  target.style.boxShadow = 'none';
                }}
              >
                {loading ? 'Starting...' : 'Begin'}
              </button>

              {/* Cancel Button */}
              <button
                onClick={handleCancel}
                disabled={loading}
                style={{
                  flex: 1,
                  padding: '12px 24px',
                  fontSize: '1rem',
                  fontWeight: 'bold',
                  background: 'rgba(255, 107, 107, 0.2)',
                  color: '#ff8888',
                  border: '2px solid rgba(255, 107, 107, 0.5)',
                  borderRadius: '8px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s ease',
                  fontFamily: 'serif',
                  letterSpacing: '0.5px',
                  opacity: loading ? 0.6 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    const target = e.currentTarget as HTMLButtonElement;
                    target.style.background = 'rgba(255, 107, 107, 0.3)';
                    target.style.boxShadow = '0 4px 12px rgba(255, 107, 107, 0.2)';
                  }
                }}
                onMouseLeave={(e) => {
                  const target = e.currentTarget as HTMLButtonElement;
                  target.style.background = 'rgba(255, 107, 107, 0.2)';
                  target.style.boxShadow = 'none';
                }}
              >
                Cancel
              </button>
            </div>

            {/* Character Count */}
            <p
              style={{
                color: '#666',
                fontSize: '0.8rem',
                marginTop: '16px',
                fontStyle: 'italic',
              }}
            >
              {playerName.length}/30 characters
            </p>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        button:disabled {
          cursor: not-allowed !important;
        }

        button:active:not(:disabled) {
          transform: scale(0.98) !important;
        }
      `}</style>
    </main>
  );
}
