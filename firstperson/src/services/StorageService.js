/**
 * StorageService.js
 * 
 * Handles local storage operations using AsyncStorage.
 * Manages conversation history, user preferences, and memory capsules.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEYS = {
    CONVERSATIONS: 'fp_conversations',
    USER_PREFS: 'fp_user_prefs',
    MEMORY_CAPSULES: 'fp_memory_capsules',
    ONBOARDING_COMPLETE: 'fp_onboarding_complete',
    SYNC_QUEUE: 'fp_sync_queue',
};

// Store a new conversation message
export async function addMessageToConversation(conversationId, message) {
    try {
        const conversations = await AsyncStorage.getItem(STORAGE_KEYS.CONVERSATIONS);
        const data = conversations ? JSON.parse(conversations) : {};

        if (!data[conversationId]) {
            data[conversationId] = [];
        }

        data[conversationId].push({
            ...message,
            timestamp: message.timestamp || new Date().toISOString(),
            id: `${conversationId}_${Date.now()}_${Math.random()}`,
        });

        await AsyncStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(data));
        return data[conversationId];
    } catch (error) {
        console.error('Error adding message to conversation:', error);
        throw error;
    }
}

// Get conversation messages
export async function getConversation(conversationId) {
    try {
        const conversations = await AsyncStorage.getItem(STORAGE_KEYS.CONVERSATIONS);
        const data = conversations ? JSON.parse(conversations) : {};
        return data[conversationId] || [];
    } catch (error) {
        console.error('Error retrieving conversation:', error);
        return [];
    }
}

// Get all conversations summary
export async function getAllConversations() {
    try {
        const conversations = await AsyncStorage.getItem(STORAGE_KEYS.CONVERSATIONS);
        const data = conversations ? JSON.parse(conversations) : {};

        return Object.entries(data).map(([id, messages]) => ({
            id,
            title: messages[0]?.text?.substring(0, 50) || 'Untitled',
            lastMessage: messages[messages.length - 1]?.text || '',
            timestamp: messages[messages.length - 1]?.timestamp || new Date().toISOString(),
            messageCount: messages.length,
        }));
    } catch (error) {
        console.error('Error retrieving all conversations:', error);
        return [];
    }
}

// Store user preferences
export async function setUserPreferences(preferences) {
    try {
        const existing = await AsyncStorage.getItem(STORAGE_KEYS.USER_PREFS);
        const data = existing ? JSON.parse(existing) : {};
        const updated = { ...data, ...preferences };
        await AsyncStorage.setItem(STORAGE_KEYS.USER_PREFS, JSON.stringify(updated));
        return updated;
    } catch (error) {
        console.error('Error setting user preferences:', error);
        throw error;
    }
}

// Get user preferences
export async function getUserPreferences() {
    try {
        const prefs = await AsyncStorage.getItem(STORAGE_KEYS.USER_PREFS);
        return prefs ? JSON.parse(prefs) : {};
    } catch (error) {
        console.error('Error retrieving user preferences:', error);
        return {};
    }
}

// Store memory capsule (relational context snapshot)
export async function createMemoryCapsule(conversationId, capsuleData) {
    try {
        const capsules = await AsyncStorage.getItem(STORAGE_KEYS.MEMORY_CAPSULES);
        const data = capsules ? JSON.parse(capsules) : {};

        const capsule = {
            id: `capsule_${Date.now()}`,
            conversationId,
            ...capsuleData,
            createdAt: new Date().toISOString(),
        };

        data[capsule.id] = capsule;
        await AsyncStorage.setItem(STORAGE_KEYS.MEMORY_CAPSULES, JSON.stringify(data));
        return capsule;
    } catch (error) {
        console.error('Error creating memory capsule:', error);
        throw error;
    }
}

// Get memory capsules for a conversation
export async function getMemoryCapsules(conversationId) {
    try {
        const capsules = await AsyncStorage.getItem(STORAGE_KEYS.MEMORY_CAPSULES);
        const data = capsules ? JSON.parse(capsules) : {};

        return Object.values(data).filter(c => c.conversationId === conversationId);
    } catch (error) {
        console.error('Error retrieving memory capsules:', error);
        return [];
    }
}

// Mark onboarding as complete
export async function setOnboardingComplete(userId) {
    try {
        await AsyncStorage.setItem(STORAGE_KEYS.ONBOARDING_COMPLETE, JSON.stringify({ userId, completedAt: new Date().toISOString() }));
    } catch (error) {
        console.error('Error setting onboarding complete:', error);
        throw error;
    }
}

// Check if onboarding is complete
export async function isOnboardingComplete() {
    try {
        const complete = await AsyncStorage.getItem(STORAGE_KEYS.ONBOARDING_COMPLETE);
        return !!complete;
    } catch (error) {
        console.error('Error checking onboarding status:', error);
        return false;
    }
}

// Add message to sync queue (for offline support)
export async function queueMessageForSync(message) {
    try {
        const queue = await AsyncStorage.getItem(STORAGE_KEYS.SYNC_QUEUE);
        const data = queue ? JSON.parse(queue) : [];
        data.push({ ...message, queuedAt: new Date().toISOString() });
        await AsyncStorage.setItem(STORAGE_KEYS.SYNC_QUEUE, JSON.stringify(data));
        return data;
    } catch (error) {
        console.error('Error queueing message for sync:', error);
        throw error;
    }
}

// Get sync queue
export async function getSyncQueue() {
    try {
        const queue = await AsyncStorage.getItem(STORAGE_KEYS.SYNC_QUEUE);
        return queue ? JSON.parse(queue) : [];
    } catch (error) {
        console.error('Error retrieving sync queue:', error);
        return [];
    }
}

// Clear sync queue after successful sync
export async function clearSyncQueue() {
    try {
        await AsyncStorage.setItem(STORAGE_KEYS.SYNC_QUEUE, JSON.stringify([]));
    } catch (error) {
        console.error('Error clearing sync queue:', error);
        throw error;
    }
}

// Clear all data (for testing/logout)
export async function clearAllData() {
    try {
        await AsyncStorage.multiRemove(Object.values(STORAGE_KEYS));
    } catch (error) {
        console.error('Error clearing all data:', error);
        throw error;
    }
}

export default {
    addMessageToConversation,
    getConversation,
    getAllConversations,
    setUserPreferences,
    getUserPreferences,
    createMemoryCapsule,
    getMemoryCapsules,
    setOnboardingComplete,
    isOnboardingComplete,
    queueMessageForSync,
    getSyncQueue,
    clearSyncQueue,
    clearAllData,
};
