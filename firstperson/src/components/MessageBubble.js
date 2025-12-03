/**
 * MessageBubble.js
 * 
 * Reusable message bubble component with prosody metadata and multimodal affect rendering.
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import MultimodalAffectDisplay from './MultimodalAffectDisplay';

export default function MessageBubble({ message, theme = 'light' }) {
    const [showMultimodal, setShowMultimodal] = useState(false);
    const {
        role,
        text,
        prosody,
        affect,
        timestamp,
    } = message;

    const isUser = role === 'user';
    const themeColors = theme === 'dark'
        ? {
            userBg: '#2a5c2a',
            assistantBg: '#3a3a3a',
            userText: '#fff',
            assistantText: '#e0e0e0',
        }
        : {
            userBg: '#DCF8C6',
            assistantBg: '#F1F0F0',
            userText: '#000',
            assistantText: '#000',
        };

    // Check if multimodal affect data exists
    const hasMultimodalData = affect && (
        affect.voice || affect.facial || affect.text || affect.fusion
    );

    return (
        <View style={[
            styles.container,
            isUser ? styles.userBubble : styles.assistantBubble,
        ]}>
            <View style={[
                styles.bubble,
                {
                    backgroundColor: isUser ? themeColors.userBg : themeColors.assistantBg,
                },
            ]}>
                <Text style={[
                    styles.text,
                    {
                        color: isUser ? themeColors.userText : themeColors.assistantText,
                    },
                ]}>
                    {text}
                </Text>

                {/* Prosody Metadata */}
                {prosody && !isUser && (
                    <View style={styles.prosodyContainer}>
                        {prosody.emotion && (
                            <Text style={styles.prosodyText}>
                                🎭 {prosody.emotion}
                                {prosody.confidence && ` (${Math.round(prosody.confidence * 100)}%)`}
                            </Text>
                        )}

                        {prosody.glyphs && prosody.glyphs.length > 0 && (
                            <View style={styles.glyphsContainer}>
                                {prosody.glyphs.slice(0, 3).map((glyph, i) => (
                                    <Text key={i} style={styles.glyphSymbol}>
                                        {glyph.symbol || '◆'}
                                    </Text>
                                ))}
                            </View>
                        )}

                        {prosody.tone && (
                            <Text style={styles.prosodyText}>
                                🎵 {prosody.tone}
                            </Text>
                        )}
                    </View>
                )}

                {/* Multimodal Affect Indicator */}
                {hasMultimodalData && !isUser && (
                    <Pressable
                        onPress={() => setShowMultimodal(!showMultimodal)}
                        style={({ pressed }) => [
                            styles.multimodalButton,
                            { opacity: pressed ? 0.7 : 1 },
                        ]}
                    >
                        <Ionicons
                            name={showMultimodal ? 'chevron-up' : 'chevron-down'}
                            size={14}
                            color="#2196F3"
                        />
                        <Text style={styles.multimodalLabel}>
                            🎯 Show Affect Analysis
                        </Text>
                    </Pressable>
                )}

                {/* Timestamp */}
                {timestamp && (
                    <Text style={styles.timestamp}>
                        {new Date(timestamp).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                        })}
                    </Text>
                )}
            </View>

            {/* Multimodal Display */}
            {hasMultimodalData && showMultimodal && !isUser && (
                <View style={styles.multimodalContainer}>
                    <MultimodalAffectDisplay affect={affect} theme={theme} />
                </View>
            )}
        </View>
        </View >
    );
}

const styles = StyleSheet.create({
    container: {
        marginVertical: 6,
        paddingHorizontal: 12,
    },
    userBubble: {
        alignItems: 'flex-end',
    },
    assistantBubble: {
        alignItems: 'flex-start',
    },
    bubble: {
        maxWidth: '85%',
        padding: 10,
        borderRadius: 12,
    },
    text: {
        fontSize: 15,
        lineHeight: 20,
    },
    prosodyContainer: {
        marginTop: 8,
        paddingTop: 8,
        borderTopWidth: 0.5,
        borderTopColor: 'rgba(0,0,0,0.1)',
    },
    prosodyText: {
        fontSize: 12,
        fontStyle: 'italic',
        marginTop: 4,
        opacity: 0.7,
    },
    glyphsContainer: {
        flexDirection: 'row',
        marginTop: 6,
        gap: 4,
    },
    glyphSymbol: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    timestamp: {
        fontSize: 11,
        marginTop: 4,
        opacity: 0.5,
    },
    multimodalButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 4,
        marginTop: 8,
        paddingTop: 8,
        borderTopWidth: 0.5,
        borderTopColor: 'rgba(33, 150, 243, 0.3)',
    },
    multimodalLabel: {
        fontSize: 12,
        color: '#2196F3',
        fontWeight: '600',
    },
    multimodalContainer: {
        marginTop: 8,
        marginLeft: 12,
        marginRight: 12,
        maxHeight: 400,
        borderRadius: 8,
        overflow: 'hidden',
    },
});
