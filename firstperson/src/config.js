const DEFAULT_API = 'http://localhost:8000';

export const SAOYNX_API_URL = (typeof process !== 'undefined' && process.env && process.env.REACT_APP_SAOYNX_API_URL)
    ? process.env.REACT_APP_SAOYNX_API_URL
    : DEFAULT_API;

export async function postMessage(text) {
    const url = `${SAOYNX_API_URL}/api/message`;
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });
        if (!res.ok) {
            const txt = await res.text();
            throw new Error(`HTTP ${res.status}: ${txt}`);
        }
        return await res.json();
    } catch (e) {
        return { error: String(e) };
    }
}

export default {
    SAOYNX_API_URL,
    postMessage,
};
