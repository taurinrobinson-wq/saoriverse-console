'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
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
      // Navigate to the first scene with player name
      router.push(`/game/velhara_market?player=${encodeURIComponent(playerName)}`);
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

  return (
    <main style={{
      position: 'relative',
      width: '100%',
      height: '100vh',
      overflow: 'hidden',
    }}>
      {/* Background Image */}
      <img
        src="/assets/backgrounds/velinor_title_eyes_closed.png"
        alt="Velinor Title"
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '88%',
          height: '88%',
          objectFit: 'contain',
          zIndex: 1,
        }}
      />

      {/* Start Button - Overlay */}
      <button
        onClick={handleStartButtonClick}
        style={{
          position: 'absolute',
          bottom: '120px',
          left: '50%',
          transform: 'translateX(-50%)',
          padding: '12.8px 32px',
          fontSize: '0.96rem',
          fontWeight: 'bold',
          background: '#2e3f2f',
          color: '#e6d8b4',
          border: '1px solid #a88f5c',
          borderRadius: '8px',
          cursor: 'pointer',
          zIndex: 10,
          transition: 'all 0.3s ease',
          boxShadow: '0 0 8px rgba(168, 143, 92, 0.3)',
          backdropFilter: 'blur(4px)',
          textShadow: '0 2px 4px rgba(0, 0, 0, 0.8)',
          fontFamily: 'serif',
          letterSpacing: '0.5px',
        }}
        onMouseEnter={(e) => {
          (e.target as HTMLButtonElement).style.background = '#3b4f3b';
          (e.target as HTMLButtonElement).style.boxShadow = '0 0 12px rgba(168, 143, 92, 0.5)';
          (e.target as HTMLButtonElement).style.transform = 'translateX(-50%) translateY(-2px)';
        }}
        onMouseLeave={(e) => {
          (e.target as HTMLButtonElement).style.background = '#2e3f2f';
          (e.target as HTMLButtonElement).style.boxShadow = '0 0 8px rgba(168, 143, 92, 0.3)';
          (e.target as HTMLButtonElement).style.transform = 'translateX(-50%)';
        }}
      >
        Start New Game
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
            background: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            backdropFilter: 'blur(2px)',
          }}
          onClick={handleCancel}
        >
          {/* Modal Content */}
          <div
            style={{
              background: 'rgba(25, 27, 30, 0.95)',
              borderRadius: '15px',
              padding: '40px',
              maxWidth: '400px',
              width: '90%',
              textAlign: 'center',
              border: '2px solid rgba(58, 109, 240, 0.6)',
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.8)',
              backdropFilter: 'blur(10px)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2
              style={{
                color: '#64b5f6',
                marginBottom: '10px',
                fontSize: '1.5rem',
                fontWeight: 'bold',
              }}
            >
              Enter Your Name
            </h2>
            <p
              style={{
                color: '#aaa',
                marginBottom: '25px',
                fontSize: '0.95rem',
              }}
            >
              Choose a name for your character in the ruins of Velhara.
            </p>

            <input
              autoFocus
              type="text"
              placeholder="Character name"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleConfirmName()}
              style={{
                width: '100%',
                padding: '12px',
                marginBottom: '20px',
                fontSize: '1rem',
                border: '2px solid rgba(58, 109, 240, 0.6)',
                borderRadius: '8px',
                background: 'rgba(30, 35, 40, 0.8)',
                color: '#fff',
                fontFamily: 'inherit',
                outline: 'none',
                transition: 'border-color 0.3s ease',
              }}
              onFocus={(e) => {
                (e.target as HTMLInputElement).style.borderColor = 'rgba(58, 109, 240, 1)';
              }}
              onBlur={(e) => {
                (e.target as HTMLInputElement).style.borderColor = 'rgba(58, 109, 240, 0.6)';
              }}
            />

            {error && (
              <div
                style={{
                  color: '#ff6b6b',
                  fontSize: '0.85rem',
                  marginBottom: '15px',
                  padding: '10px',
                  background: 'rgba(255, 107, 107, 0.1)',
                  borderRadius: '6px',
                  border: '1px solid rgba(255, 107, 107, 0.6)',
                }}
              >
                {error}
              </div>
            )}

            <div
              style={{
                display: 'flex',
                gap: '12px',
                justifyContent: 'center',
              }}
            >
              <button
                onClick={handleConfirmName}
                disabled={loading}
                style={{
                  flex: 1,
                  padding: '12px',
                  fontSize: '1rem',
                  background: loading ? '#666' : 'rgba(74, 169, 108, 0.8)',
                  color: '#fff',
                  border: '2px solid rgba(74, 169, 108, 0.8)',
                  borderRadius: '8px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold',
                  transition: 'all 0.3s ease',
                  opacity: loading ? 0.7 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    (e.target as HTMLButtonElement).style.background = 'rgba(56, 158, 89, 0.95)';
                    (e.target as HTMLButtonElement).style.transform = 'translateY(-2px)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!loading) {
                    (e.target as HTMLButtonElement).style.background = 'rgba(74, 169, 108, 0.8)';
                    (e.target as HTMLButtonElement).style.transform = 'translateY(0)';
                  }
                }}
              >
                {loading ? 'Starting...' : 'Confirm'}
              </button>
              <button
                onClick={handleCancel}
                disabled={loading}
                style={{
                  flex: 1,
                  padding: '12px',
                  fontSize: '1rem',
                  background: 'rgba(150, 150, 150, 0.6)',
                  color: '#fff',
                  border: '2px solid rgba(150, 150, 150, 0.8)',
                  borderRadius: '8px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold',
                  transition: 'all 0.3s ease',
                  opacity: loading ? 0.5 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    (e.target as HTMLButtonElement).style.background = 'rgba(120, 120, 120, 0.8)';
                    (e.target as HTMLButtonElement).style.transform = 'translateY(-2px)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!loading) {
                    (e.target as HTMLButtonElement).style.background = 'rgba(150, 150, 150, 0.6)';
                    (e.target as HTMLButtonElement).style.transform = 'translateY(0)';
                  }
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
