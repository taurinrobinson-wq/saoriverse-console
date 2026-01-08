// Default is localhost, but when running in Expo on a physical device
// `localhost` refers to the device itself. Try to auto-detect the
// dev machine IP using `expo-constants` (debuggerHost) when available.
let DEFAULT_API = 'http://localhost:8000';
try {
    // `expo-constants` is available in Expo-managed projects
    // and provides the `manifest.debuggerHost` value when running
    // the Metro bundler. It looks like "192.168.1.100:8081".
    const Constants = require('expo-constants');
    const manifest = Constants && (Constants.manifest || Constants.manifest2);
    const debuggerHost = manifest && (manifest.debuggerHost || (manifest.server && manifest.server.url));
    if (debuggerHost) {
        const host = String(debuggerHost).split(':')[0];
        if (host && host !== 'localhost' && host !== '127.0.0.1') {
            DEFAULT_API = `http://${host}:8000`;
        }
    }
} catch (e) {
    // ignore — fall back to localhost
}

export const SAOYNX_API_URL = (typeof process !== 'undefined' && process.env && process.env.REACT_APP_SAOYNX_API_URL)
    ? process.env.REACT_APP_SAOYNX_API_URL
    : DEFAULT_API;

// Post a message to the FastAPI backend. The FastAPI app expects `message`, `mode`, and `user_id`.
export async function postMessage(text, { user_id = 'anon', mode = 'local' } = {}) {
    const url = `${SAOYNX_API_URL}/api/chat`;
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: text, mode, user_id }),
        });
        if (!res.ok) {
            const txt = await res.text();
            throw new Error(`HTTP ${res.status}: ${txt}`);
        }
        const data = await res.json();
        // FastAPI returns { success: True/False, reply, glyph, processing_time }
        if (data && data.success) return { reply: data.reply, glyph: data.glyph, processing_time: data.processing_time };
        return { error: data && data.reply ? data.reply : 'Unknown error from backend' };
    } catch (e) {
        return { error: String(e) };
    }
}

export default {
    SAOYNX_API_URL,
    postMessage,
};
