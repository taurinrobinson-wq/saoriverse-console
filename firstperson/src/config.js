const DEFAULT_API = 'http://localhost:8000';

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
