// Configuration for Saoynx API endpoint used by the MessageOverlay screen.
// Update `SAOYNX_API_URL` to point to your Saoynx backend.
export const SAOYNX_API_URL = 'https://your-backend.example.com/api';

export async function postMessage(payload) {
    try {
        const res = await fetch(SAOYNX_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        return { ok: res.ok, data };
    } catch (err) {
        return { ok: false, error: err.message || String(err) };
    }
}
