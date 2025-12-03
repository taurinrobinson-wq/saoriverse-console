/**
 * ChatScreen.js
 * 
 * Main chat interface with prosody features, memory capsule support,
 * and multi-turn conversation management.
 */

import React, { useState, useEffect, useRef } from 'react';
import {
    View,
    ScrollView,
    Text,
    StyleSheet,
    SafeAreaView,
    ActivityIndicator,
} from 'react-native';
import MessageBubble from '../components/MessageBubble';
import MultimodalInput from '../components/MultimodalInput';
import * as ApiService from '../services/ApiService';
import * as StorageService from '../services/StorageService';

export default function ChatScreen({ route, navigation }) {
    const conversationId = route?.params?.conversationId || 'default';

    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isLoadingHistory, setIsLoadingHistory] = useState(true);
    const scrollRef = useRef(null);

    // Load conversation history on mount
    useEffect(() => {
        loadConversationHistory();
    }, [conversationId]);

    // Scroll to bottom when new messages arrive
    useEffect(() => {
        if (messages.length > 0) {
            setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);
        }
    }, [messages]);

    const loadConversationHistory = async () => {
        try {
            setIsLoadingHistory(true);
            const history = await StorageService.getConversation(conversationId);
            setMessages(history);
        } catch (error) {
            console.error('Error loading conversation:', error);
        } finally {
            setIsLoadingHistory(false);
        }
    };

    const handleSendMessage = async (text) => {
        if (!text.trim()) return;

        // Add user message immediately
        const userMessage = {
            role: 'user',
            text,
            timestamp: new Date().toISOString(),
        };

        setMessages(prev => [...prev, userMessage]);

        // Save user message to storage
        try {
            await StorageService.addMessageToConversation(conversationId, userMessage);
        } catch (error) {
            console.error('Error saving user message:', error);
        }

        // Send to backend
        setLoading(true);
        try {
            const result = await ApiService.sendMessage(text, {
                userId: 'anon',
                mode: 'local',
                conversationId,
                context: { previousMessages: messages.length },
            });

            if (result.success) {
                const assistantMessage = {
                    role: 'assistant',
                    text: result.reply,
                    prosody: result.prosody,
                    affect: result.affect,
                    timestamp: new Date().toISOString(),
                };

                setMessages(prev => [...prev, assistantMessage]);

                // Save assistant message to storage
                try {
                    await StorageService.addMessageToConversation(conversationId, assistantMessage);
                } catch (error) {
                    console.error('Error saving assistant message:', error);
                }

                // Create memory capsule periodically (every 5 messages)
                if (messages.length % 5 === 0) {
                    try {
                        await StorageService.createMemoryCapsule(conversationId, {
                            messageCount: messages.length,
                            lastContext: text.substring(0, 100),
                            prosodySnapshot: result.prosody,
                        });
                    } catch (error) {
                        console.error('Error creating memory capsule:', error);
                    }
                }
            } else if (result.offline) {
                // Message was queued for offline sync
                const offlineMessage = {
                    role: 'system',
                    text: '📡 Message queued. Will send when connection restored.',
                    timestamp: new Date().toISOString(),
                    offline: true,
                };
                setMessages(prev => [...prev, offlineMessage]);
            } else {
                // Error occurred
                const errorMessage = {
                    role: 'system',
                    text: `❌ Error: ${result.error}`,
                    timestamp: new Date().toISOString(),
                    isError: true,
                };
                setMessages(prev => [...prev, errorMessage]);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                role: 'system',
                text: `❌ Error: ${String(error)}`,
                timestamp: new Date().toISOString(),
                isError: true,
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleMultimodalMessage = async (messageData) => {
        const { type, content } = messageData;

        switch (type) {
            case 'text':
                handleSendMessage(content);
                break;
            case 'voice':
                // Send to voice affect detector backend
                console.log('Voice message:', content);
                // TODO: Call ApiService.analyzeVoice(content)
                break;
            case 'facial':
                // Send to facial expression detector backend
                console.log('Facial message:', content);
                // TODO: Call ApiService.analyzeFacial(content)
                break;
            default:
                console.warn('Unknown message type:', type);
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>FirstPerson</Text>
                <Text style={styles.subtitle}>Emotional AI Companion</Text>
            </View>

            {isLoadingHistory ? (
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color="#007AFF" />
                    <Text style={styles.loadingText}>Loading conversation...</Text>
                </View>
            ) : (
                <>
                    <ScrollView
                        style={styles.messagesContainer}
                        ref={scrollRef}
                        contentContainerStyle={styles.messagesContent}
                    >
                        {messages.length === 0 && (
                            <View style={styles.emptyContainer}>
                                <Text style={styles.emptyText}>
                                    Begin your conversation with FirstPerson...
                                </Text>
                            </View>
                        )}
                        {messages.map((message, index) => (
                            <MessageBubble
                                key={index}
                                message={message}
                            />
                        ))}
                    </ScrollView>

                    <MultimodalInput
                        onSendMessage={handleMultimodalMessage}
                        disabled={isLoadingHistory || loading}
                    />
                </>
            )}
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
    },
    header: {
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0',
    },
    title: {
        fontSize: 20,
        fontWeight: '700',
        color: '#000',
    },
    subtitle: {
        fontSize: 12,
        color: '#666',
        marginTop: 2,
    },
    messagesContainer: {
        flex: 1,
    },
    messagesContent: {
        paddingVertical: 8,
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    emptyText: {
        fontSize: 16,
        color: '#999',
        textAlign: 'center',
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    loadingText: {
        marginTop: 12,
        fontSize: 14,
        color: '#666',
    },
});
