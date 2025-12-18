"use client";

import { useState, CSSProperties } from "react";

interface AuthModalProps {
  onClose: () => void;
}

export default function AuthModal({ onClose }: AuthModalProps) {
  const [mode, setMode] = useState<'login'|'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const api = (path: string, body: any) =>
    fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).then(async (r) => ({ ok: r.ok, status: r.status, json: await r.json().catch(()=>({})) }));

  const handleSubmit = async () => {
    setError('');
    if (!username || !password) { setError('username and password required'); return; }
    setLoading(true);
    try {
      const path = mode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const res = await api(path, { username, password });
      if (!res.ok) {
        setError(res.json?.detail || `Error ${res.status}`);
        setLoading(false);
        return;
      }
      const token = res.json?.access_token || null;
      if (token) {
        localStorage.setItem('velinor_token', token);
      }
      onClose();
    } catch (e) {
      setError('Network error');
    } finally { setLoading(false); }
  };

  const backdrop: CSSProperties = {
    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200
  };

  return (
    <div style={backdrop} onClick={onClose}>
      <div style={{ background: '#111', padding: 24, borderRadius: 12, width: 360 }} onClick={(e)=>e.stopPropagation()}>
        <h3 style={{ color: '#e6d8b4', marginTop: 0 }}>{mode === 'login' ? 'Sign in' : 'Register'}</h3>
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          <button onClick={()=>setMode('login')} style={{ flex: 1, padding: 8, background: mode==='login'? '#254d25':'#222', color: '#e6d8b4', borderRadius: 6 }}>Login</button>
          <button onClick={()=>setMode('register')} style={{ flex: 1, padding: 8, background: mode==='register'? '#254d25':'#222', color: '#e6d8b4', borderRadius: 6 }}>Register</button>
        </div>
        <input value={username} onChange={e=>setUsername(e.target.value)} placeholder="username" style={{ width: '100%', padding: 8, marginBottom: 8, borderRadius: 6 }} />
        <input value={password} onChange={e=>setPassword(e.target.value)} placeholder="password" type="password" style={{ width: '100%', padding: 8, marginBottom: 8, borderRadius: 6 }} />
        {error && <div style={{ color: '#ff6b6b', marginBottom: 8 }}>{error}</div>}
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={handleSubmit} disabled={loading} style={{ flex: 1, padding: 10, borderRadius: 8, background: '#2e3f2f', color: '#e6d8b4' }}>{loading ? 'Please wait...' : (mode==='login'? 'Sign in':'Create')}</button>
          <button onClick={onClose} style={{ padding: 10, borderRadius: 8, background: '#222', color: '#e6d8b4' }}>Close</button>
        </div>
      </div>
    </div>
  );
}
