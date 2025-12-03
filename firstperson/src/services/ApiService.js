/**
 * ApiService.js
 * 
 * Enhanced API integration with error handling, metadata parsing, and offline support.
 */

import { SAOYNX_API_URL } from '../config';
import * as StorageService from './StorageService';

export const API_ENDPOINTS = {
    CHAT: '/api/chat',
    HISTORY: '/api/conversation/history',
    GLYPHS: '/api/glyphs',
    EMOTIONS: '/api/emotions',
};

/**
 * Send a message to the FirstPerson backend
 */
export async function sendMessage(text, options = {}) {
    const {
        userId = 'anon',
        mode = 'local',
        conversationId = 'default',
        context = {},
        timeout = 30000, // 30 second timeout
    } = options;

    const url = `${SAOYNX_API_URL}${API_ENDPOINTS.CHAT}`;

    try {
        // Create abort controller for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const res = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: text,
                mode,
                user_id: userId,
                conversation_id: conversationId,
                context,
            }),
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!res.ok) {
            const txt = await res.text();
            throw new Error(`HTTP ${res.status}: ${txt}`);
        }

        const data = await res.json();

        // Parse response and extract prosody metadata + multimodal affect
        if (data && data.success) {
            return {
                success: true,
                reply: data.reply || '',
                prosody: parseProsodyMetadata(data),
                affect: parseMultimodalAffect(data),
                processingTime: data.processing_time || 0,
                glyphs: data.glyphs || [],
                emotion: data.emotion || null,
                confidence: data.confidence || null,
                rawResponse: data,
            };
        }

        return {
            success: false,
            error: data?.reply || 'Unknown error from backend',
            rawResponse: data,
        };
    } catch (error) {
        // Queue for offline sync on network error
        if (isNetworkError(error)) {
            await StorageService.queueMessageForSync({
                text,
                userId,
                mode,
                conversationId,
                context,
                failedAt: new Date().toISOString(),
            });

            return {
                success: false,
                error: 'Network unavailable. Message queued for sync.',
                offline: true,
            };
        }

        return {
            success: false,
            error: String(error),
            offline: false,
        };
    }
}

/**
 * Get conversation history from backend
 */
export async function getConversationHistory(conversationId, options = {}) {
    const { userId = 'anon' } = options;
    const url = `${SAOYNX_API_URL}${API_ENDPOINTS.HISTORY}?conversation_id=${conversationId}&user_id=${userId}`;

    try {
        const res = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        return {
            success: true,
            messages: data.messages || [],
            rawResponse: data,
        };
    } catch (error) {
        console.error('Error fetching conversation history:', error);
        return {
            success: false,
            error: String(error),
            messages: [],
        };
    }
}

/**
 * Get available glyphs from backend
 */
export async function getGlyphs(options = {}) {
    const { limit = 50, offset = 0 } = options;
    const url = `${SAOYNX_API_URL}${API_ENDPOINTS.GLYPHS}?limit=${limit}&offset=${offset}`;

    try {
        const res = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        return {
            success: true,
            glyphs: data.glyphs || [],
            total: data.total || 0,
        };
    } catch (error) {
        console.error('Error fetching glyphs:', error);
        return {
            success: false,
            error: String(error),
            glyphs: [],
        };
    }
}

/**
 * Parse prosody metadata from backend response
 */
function parseProsodyMetadata(response) {
    return {
        emotion: response.emotion || null,
        confidence: response.confidence || null,
        intensity: response.intensity || 'neutral',
        tone: response.tone || null,
        ritual: response.ritual || null,
        glyphs: response.glyphs ? response.glyphs.map(g => ({
            name: g.name || g.glyph_name || 'Unknown',
            score: g.score || g.confidence || 0,
            symbol: g.symbol || '◆',
            description: g.description || '',
        })) : [],
    };
}

/**
 * Parse multimodal affect data from backend response
 * Extracts voice, facial, text, and fusion affect detection results
 */
function parseMultimodalAffect(response) {
    // Return null if no multimodal data present
    if (!response.affect && !response.voice_affect && !response.facial_affect && !response.text_affect) {
        return null;
    }

    // If affect is already structured, use it; otherwise construct from components
    if (response.affect) {
        return {
            voice: response.affect.voice || null,
            facial: response.affect.facial || null,
            text: response.affect.text || null,
            fusion: response.affect.fusion || null,
            timestamp: response.affect.timestamp || new Date().toISOString(),
        };
    }

    // Construct from individual components if present
    const hasAnyAffect = response.voice_affect || response.facial_affect || response.text_affect;
    if (!hasAnyAffect) return null;

    return {
        voice: response.voice_affect ? {
            emotion: response.voice_affect.emotion || 'neutral',
            arousal: response.voice_affect.arousal || 0.5,
            valence: response.voice_affect.valence || 0.5,
            confidence: response.voice_affect.confidence || 0.5,
            prosodic_features: response.voice_affect.prosodic_features || {},
        } : null,
        facial: response.facial_affect ? {
            emotion: response.facial_affect.emotion || 'neutral',
            intensity: response.facial_affect.intensity || 0.5,
            confidence: response.facial_affect.confidence || 0.5,
            detected_features: response.facial_affect.detected_features || [],
        } : null,
        text: response.text_affect ? {
            emotion: response.text_affect.emotion || 'neutral',
            intensity: response.text_affect.intensity || 0.5,
            sentiment: response.text_affect.sentiment || 0.5,
            confidence: response.text_affect.confidence || 0.5,
        } : null,
        fusion: response.text_affect ? {
            primary_emotion: response.text_affect.emotion || 'neutral',
            confidence: response.text_affect.confidence || 0.5,
            arousal: response.voice_affect?.arousal || 0.5,
            valence: response.voice_affect?.valence || 0.5,
        } : null,
        timestamp: new Date().toISOString(),
    };
}

/**
 * Check if error is network-related
 */
function isNetworkError(error) {
    const networkErrors = [
        'Network request failed',
        'Failed to fetch',
        'NetworkError',
        'TypeError: Network request failed',
        'ECONNREFUSED',
        'ENOTFOUND',
    ];
    return networkErrors.some(e => String(error).includes(e));
}

/**
 * Test backend connectivity
 */
export async function testConnectivity() {
    try {
        const res = await fetch(`${SAOYNX_API_URL}/health`, {
            method: 'GET',
            timeout: 5000,
        });
        return res.ok;
    } catch (error) {
        return false;
    }
}

export default {
    sendMessage,
    getConversationHistory,
    getGlyphs,
    testConnectivity,
    API_ENDPOINTS,
};
