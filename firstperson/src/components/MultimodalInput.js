/**
 * MultimodalInput.js
 * 
 * Input component with multimodal capture: text, voice recording, and camera for facial expression.
 * Integrates with voice_affect_detector and facial_expression_detector backends.
 */

import React, { useState, useRef } from 'react';
import {
    View,
    Text,
    StyleSheet,
    Pressable,
    TextInput,
    Alert,
    ActivityIndicator,
} from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import * as DocumentPicker from 'expo-document-picker';

export default function MultimodalInput({ onSendMessage, theme = 'light', disabled = false }) {
    const [text, setText] = useState('');
    const [recordingMode, setRecordingMode] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [cameraMode, setCameraMode] = useState(false);
    const [loading, setLoading] = useState(false);

    const themeColors = theme === 'dark'
        ? {
            bg: '#2a2a2a',
            border: '#444',
            text: '#e0e0e0',
            accent: '#64B5F6',
        }
        : {
            bg: '#fff',
            border: '#e0e0e0',
            text: '#333',
            accent: '#2196F3',
        };

    const handleSendText = () => {
        if (text.trim()) {
            onSendMessage({
                type: 'text',
                content: text,
            });
            setText('');
        }
    };

    const handleStartRecording = () => {
        setRecordingMode(true);
        setIsRecording(true);
        // In a real implementation, use expo-av or react-native-audio-recording
        // For now, this shows the UI pattern
    };

    const handleStopRecording = async () => {
        setIsRecording(false);
        // Send recording to backend for voice_affect_detector analysis
        onSendMessage({
            type: 'voice',
            content: 'audio_uri', // Would be actual audio file URI
        });
        setRecordingMode(false);
    };

    const handleCameraCapture = () => {
        setCameraMode(true);
        // In a real implementation, use expo-camera
        // Capture selfie for facial expression analysis
    };

    const handleCameraDone = async () => {
        // Send image to backend for facial_expression_detector analysis
        onSendMessage({
            type: 'facial',
            content: 'image_uri', // Would be actual image file URI
        });
        setCameraMode(false);
    };

    const handleAddAttachment = async () => {
        try {
            const result = await DocumentPicker.getDocumentAsync({
                type: 'audio/*',
            });

            if (result.type === 'success') {
                onSendMessage({
                    type: 'voice',
                    content: result.uri,
                });
            }
        } catch (error) {
            Alert.alert('Error', 'Failed to pick audio file');
        }
    };

    return (
        <View style={[styles.container, { backgroundColor: themeColors.bg }]}>
            {/* Multimodal Mode Selector */}
            {!recordingMode && !cameraMode && (
                <View style={styles.modeSelector}>
                    <Pressable
                        onPress={() => setRecordingMode(true)}
                        disabled={disabled}
                        style={({ pressed }) => [
                            styles.modeButton,
                            { opacity: disabled || pressed ? 0.6 : 1 },
                        ]}
                    >
                        <Ionicons name="mic" size={20} color={themeColors.accent} />
                        <Text style={[styles.modeLabel, { color: themeColors.text }]}>
                            Voice
                        </Text>
                    </Pressable>

                    <Pressable
                        onPress={handleCameraCapture}
                        disabled={disabled}
                        style={({ pressed }) => [
                            styles.modeButton,
                            { opacity: disabled || pressed ? 0.6 : 1 },
                        ]}
                    >
                        <Ionicons name="camera" size={20} color={themeColors.accent} />
                        <Text style={[styles.modeLabel, { color: themeColors.text }]}>
                            Facial
                        </Text>
                    </Pressable>

                    <Pressable
                        onPress={handleAddAttachment}
                        disabled={disabled}
                        style={({ pressed }) => [
                            styles.modeButton,
                            { opacity: disabled || pressed ? 0.6 : 1 },
                        ]}
                    >
                        <MaterialCommunityIcons
                            name="file-audio"
                            size={20}
                            color={themeColors.accent}
                        />
                        <Text style={[styles.modeLabel, { color: themeColors.text }]}>
                            Upload
                        </Text>
                    </Pressable>
                </View>
            )}

            {/* Text Input + Send */}
            <View style={[
                styles.inputContainer,
                { borderColor: themeColors.border, backgroundColor: themeColors.bg },
            ]}>
                <TextInput
                    style={[
                        styles.textInput,
                        { color: themeColors.text, borderColor: themeColors.border },
                    ]}
                    placeholder="Type a message..."
                    placeholderTextColor={themeColors.text}
                    value={text}
                    onChangeText={setText}
                    editable={!disabled && !recordingMode && !cameraMode}
                    multiline
                />

                <Pressable
                    onPress={handleSendText}
                    disabled={disabled || !text.trim() || recordingMode || cameraMode}
                    style={({ pressed }) => [
                        styles.sendButton,
                        { opacity: disabled || !text.trim() || pressed ? 0.6 : 1 },
                    ]}
                >
                    <Ionicons
                        name="send"
                        size={20}
                        color={text.trim() ? themeColors.accent : '#999'}
                    />
                </Pressable>
            </View>

            {/* Voice Recording UI */}
            {recordingMode && (
                <View style={styles.recordingPanel}>
                    <View style={styles.recordingHeader}>
                        <Text style={[styles.recordingTitle, { color: themeColors.text }]}>
                            🎤 Voice Message
                        </Text>
                        <Pressable
                            onPress={() => {
                                setRecordingMode(false);
                                setIsRecording(false);
                            }}
                        >
                            <Ionicons name="close" size={24} color={themeColors.text} />
                        </Pressable>
                    </View>

                    {isRecording ? (
                        <View style={styles.recordingContent}>
                            <View style={styles.waveformContainer}>
                                <View style={[styles.waveform, { backgroundColor: '#FF6B6B' }]} />
                                <View style={[styles.waveform, { backgroundColor: '#FF8E8E' }]} />
                                <View style={[styles.waveform, { backgroundColor: '#FF6B6B' }]} />
                                <View style={[styles.waveform, { backgroundColor: '#FF8E8E' }]} />
                                <View style={[styles.waveform, { backgroundColor: '#FF6B6B' }]} />
                            </View>
                            <Text style={[styles.recordingStatus, { color: '#FF6B6B' }]}>
                                Recording... 0:23
                            </Text>
                        </View>
                    ) : (
                        <View style={styles.recordingContent}>
                            <Text style={[styles.recordingInfo, { color: themeColors.text }]}>
                                Ready to record. Click start when ready.
                            </Text>
                        </View>
                    )}

                    <View style={styles.recordingControls}>
                        <Pressable
                            onPress={handleStartRecording}
                            disabled={isRecording}
                            style={({ pressed }) => [
                                styles.recordButton,
                                {
                                    backgroundColor: isRecording ? '#ddd' : '#4CAF50',
                                    opacity: pressed ? 0.7 : 1,
                                },
                            ]}
                        >
                            <Ionicons
                                name="play-circle"
                                size={20}
                                color="#fff"
                            />
                            <Text style={styles.recordButtonText}>Start</Text>
                        </Pressable>

                        <Pressable
                            onPress={handleStopRecording}
                            disabled={!isRecording}
                            style={({ pressed }) => [
                                styles.recordButton,
                                {
                                    backgroundColor: isRecording ? '#FF6B6B' : '#ddd',
                                    opacity: pressed ? 0.7 : 1,
                                },
                            ]}
                        >
                            <Ionicons
                                name="stop-circle"
                                size={20}
                                color="#fff"
                            />
                            <Text style={styles.recordButtonText}>Stop & Send</Text>
                        </Pressable>
                    </View>
                </View>
            )}

            {/* Camera UI */}
            {cameraMode && (
                <View style={styles.cameraPanel}>
                    <View style={styles.cameraHeader}>
                        <Text style={[styles.cameraTitle, { color: themeColors.text }]}>
                            📸 Capture Expression
                        </Text>
                        <Pressable onPress={() => setCameraMode(false)}>
                            <Ionicons name="close" size={24} color={themeColors.text} />
                        </Pressable>
                    </View>

                    <View style={styles.cameraPlaceholder}>
                        <Ionicons name="camera" size={60} color="#999" />
                        <Text style={[styles.cameraPlaceholderText, { color: themeColors.text }]}>
                            (Camera preview would appear here)
                        </Text>
                    </View>

                    <View style={styles.cameraControls}>
                        <Pressable
                            onPress={handleCameraDone}
                            style={({ pressed }) => [
                                styles.captureButton,
                                { opacity: pressed ? 0.7 : 1 },
                            ]}
                        >
                            <Ionicons name="checkmark-circle" size={20} color="#fff" />
                            <Text style={styles.captureButtonText}>Capture & Send</Text>
                        </Pressable>
                    </View>
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        paddingHorizontal: 12,
        paddingVertical: 8,
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
    },
    modeSelector: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        marginBottom: 12,
        paddingVertical: 8,
    },
    modeButton: {
        alignItems: 'center',
        gap: 4,
        paddingVertical: 6,
        paddingHorizontal: 12,
    },
    modeLabel: {
        fontSize: 11,
        fontWeight: '600',
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        borderWidth: 1,
        borderRadius: 24,
        paddingLeft: 16,
        paddingRight: 8,
        gap: 8,
    },
    textInput: {
        flex: 1,
        paddingVertical: 10,
        fontSize: 14,
        maxHeight: 100,
    },
    sendButton: {
        paddingRight: 8,
        paddingVertical: 8,
    },
    recordingPanel: {
        marginTop: 12,
        borderRadius: 12,
        overflow: 'hidden',
        backgroundColor: '#f5f5f5',
        borderWidth: 1,
        borderColor: '#e0e0e0',
    },
    recordingHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0',
    },
    recordingTitle: {
        fontSize: 14,
        fontWeight: '600',
    },
    recordingContent: {
        alignItems: 'center',
        paddingVertical: 24,
    },
    waveformContainer: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        gap: 3,
        height: 40,
        marginBottom: 12,
    },
    waveform: {
        width: 4,
        height: '60%',
        borderRadius: 2,
    },
    recordingStatus: {
        fontSize: 12,
        fontWeight: '600',
    },
    recordingInfo: {
        fontSize: 12,
    },
    recordingControls: {
        flexDirection: 'row',
        gap: 8,
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
    },
    recordButton: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 6,
        paddingVertical: 10,
        borderRadius: 8,
    },
    recordButtonText: {
        color: '#fff',
        fontSize: 13,
        fontWeight: '600',
    },
    cameraPanel: {
        marginTop: 12,
        borderRadius: 12,
        overflow: 'hidden',
        backgroundColor: '#f5f5f5',
        borderWidth: 1,
        borderColor: '#e0e0e0',
    },
    cameraHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0',
    },
    cameraTitle: {
        fontSize: 14,
        fontWeight: '600',
    },
    cameraPlaceholder: {
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 60,
        backgroundColor: '#f0f0f0',
    },
    cameraPlaceholderText: {
        fontSize: 12,
        marginTop: 12,
    },
    cameraControls: {
        flexDirection: 'row',
        gap: 8,
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
    },
    captureButton: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 6,
        paddingVertical: 10,
        borderRadius: 8,
        backgroundColor: '#2196F3',
    },
    captureButtonText: {
        color: '#fff',
        fontSize: 13,
        fontWeight: '600',
    },
});
