/**
 * MessageBubble.js
 * 
 * Reusable message bubble component with prosody metadata rendering.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function MessageBubble({ message, theme = 'light' }) {
    const {
        role,
        text,
        prosody,
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
        </View>
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
});
