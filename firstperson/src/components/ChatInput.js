/**
 * ChatInput.js
 * 
 * Enhanced chat input component with multi-line support and sending state.
 */

import React, { useState } from 'react';
import {
    View,
    TextInput,
    TouchableOpacity,
    ActivityIndicator,
    StyleSheet,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function ChatInput({
    onSend,
    disabled = false,
    loading = false,
    placeholder = 'Type a message...',
}) {
    const [input, setInput] = useState('');

    const handleSend = () => {
        if (!input.trim() || disabled || loading) return;

        onSend(input.trim());
        setInput('');
    };

    return (
        <View style={styles.container}>
            <TextInput
                value={input}
                onChangeText={setInput}
                placeholder={placeholder}
                placeholderTextColor="#999"
                style={styles.input}
                multiline
                maxLength={2000}
                editable={!disabled && !loading}
            />

            <TouchableOpacity
                onPress={handleSend}
                disabled={!input.trim() || disabled || loading}
                style={[
                    styles.sendButton,
                    (!input.trim() || disabled || loading) && styles.sendButtonDisabled,
                ]}
            >
                {loading ? (
                    <ActivityIndicator size="small" color="#fff" />
                ) : (
                    <Ionicons name="send" size={20} color="#fff" />
                )}
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        gap: 8,
        padding: 12,
        backgroundColor: '#f9f9f9',
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
    },
    input: {
        flex: 1,
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 20,
        paddingHorizontal: 16,
        paddingVertical: 10,
        fontSize: 15,
        maxHeight: 100,
        backgroundColor: '#fff',
    },
    sendButton: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#007AFF',
        justifyContent: 'center',
        alignItems: 'center',
    },
    sendButtonDisabled: {
        opacity: 0.5,
    },
});
