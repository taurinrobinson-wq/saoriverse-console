/**
 * SyncService.js
 * 
 * Handles offline-first synchronization of messages and data.
 * Detects connection status and auto-syncs when online.
 */

import * as StorageService from './StorageService';
import * as ApiService from './ApiService';

let syncListeners = [];
let isSyncing = false;

/**
 * Subscribe to sync status changes
 */
export function onSyncStatusChange(callback) {
    syncListeners.push(callback);
    return () => {
        syncListeners = syncListeners.filter(cb => cb !== callback);
    };
}

/**
 * Notify all listeners of sync status change
 */
function notifySyncStatusChange(status) {
    syncListeners.forEach(cb => cb(status));
}

/**
 * Perform full sync of queued messages
 */
export async function performSync() {
    if (isSyncing) return { success: false, message: 'Sync already in progress' };

    isSyncing = true;
    notifySyncStatusChange({ syncing: true });

    try {
        const queue = await StorageService.getSyncQueue();

        if (queue.length === 0) {
            notifySyncStatusChange({ syncing: false, syncedCount: 0 });
            return { success: true, syncedCount: 0 };
        }

        let syncedCount = 0;
        const errors = [];

        for (const queuedMessage of queue) {
            try {
                const result = await ApiService.sendMessage(queuedMessage.text, {
                    userId: queuedMessage.userId,
                    mode: queuedMessage.mode,
                    conversationId: queuedMessage.conversationId,
                    context: queuedMessage.context,
                });

                if (result.success) {
                    // Add both user message and assistant response to conversation
                    await StorageService.addMessageToConversation(
                        queuedMessage.conversationId,
                        {
                            role: 'user',
                            text: queuedMessage.text,
                            timestamp: queuedMessage.queuedAt,
                            synced: true,
                            prosody: result.prosody,
                        }
                    );

                    await StorageService.addMessageToConversation(
                        queuedMessage.conversationId,
                        {
                            role: 'assistant',
                            text: result.reply,
                            timestamp: new Date().toISOString(),
                            prosody: result.prosody,
                            glyphs: result.glyphs,
                        }
                    );

                    syncedCount++;
                } else {
                    errors.push({
                        message: queuedMessage.text,
                        error: result.error,
                    });
                }
            } catch (error) {
                errors.push({
                    message: queuedMessage.text,
                    error: String(error),
                });
            }
        }

        // Clear sync queue after processing
        if (syncedCount > 0) {
            await StorageService.clearSyncQueue();
        }

        notifySyncStatusChange({
            syncing: false,
            syncedCount,
            errors: errors.length > 0 ? errors : null,
        });

        return {
            success: errors.length === 0,
            syncedCount,
            errors: errors.length > 0 ? errors : null,
        };
    } catch (error) {
        notifySyncStatusChange({
            syncing: false,
            error: String(error),
        });

        return {
            success: false,
            error: String(error),
        };
    } finally {
        isSyncing = false;
    }
}

/**
 * Check current sync status
 */
export async function getSyncStatus() {
    const queue = await StorageService.getSyncQueue();
    return {
        syncing: isSyncing,
        queuedMessages: queue.length,
    };
}

export default {
    performSync,
    getSyncStatus,
    onSyncStatusChange,
};
