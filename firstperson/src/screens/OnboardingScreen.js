/**
 * OnboardingScreen.js
 * 
 * Guided first-use flow with ritual, casual, or reflective mode selection.
 * Stores user preferences for future sessions.
 */

import React, { useState } from 'react';
import {
    View,
    Text,
    TouchableOpacity,
    StyleSheet,
    SafeAreaView,
    ScrollView,
    Animated,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as StorageService from '../services/StorageService';

const FIRST_TURN_MODES = [
    {
        id: 'ritual',
        name: 'Ritual',
        icon: '🕯️',
        description: 'Begin with a guided reflection ritual',
        color: '#8B6F47',
    },
    {
        id: 'casual',
        name: 'Casual',
        icon: '💬',
        description: 'Jump into a relaxed conversation',
        color: '#4A90E2',
    },
    {
        id: 'reflective',
        name: 'Reflective',
        icon: '🧘',
        description: 'Explore deeper emotional themes',
        color: '#7B68EE',
    },
];

export default function OnboardingScreen({ navigation }) {
    const [step, setStep] = useState(0); // 0: Welcome, 1: Mode Selection, 2: Personalization
    const [selectedMode, setSelectedMode] = useState(null);
    const [userName, setUserName] = useState('');

    const handleModeSelect = (modeId) => {
        setSelectedMode(modeId);
    };

    const handleContinue = async () => {
        if (step < 2) {
            setStep(step + 1);
        } else {
            // Save preferences and complete onboarding
            try {
                const prefs = {
                    firstTurnMode: selectedMode,
                    userName: userName || 'Friend',
                    onboardedAt: new Date().toISOString(),
                };
                await StorageService.setUserPreferences(prefs);
                await StorageService.setOnboardingComplete('anon');

                navigation.reset({
                    index: 0,
                    routes: [{ name: 'Chat' }],
                });
            } catch (error) {
                console.error('Error completing onboarding:', error);
            }
        }
    };

    const handleSkip = async () => {
        try {
            await StorageService.setOnboardingComplete('anon');
            navigation.reset({
                index: 0,
                routes: [{ name: 'Chat' }],
            });
        } catch (error) {
            console.error('Error skipping onboarding:', error);
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
                {/* Step 1: Welcome */}
                {step === 0 && (
                    <View style={styles.step}>
                        <View style={styles.iconLarge}>
                            <Text style={styles.iconText}>🧠</Text>
                        </View>
                        <Text style={styles.title}>Welcome to FirstPerson</Text>
                        <Text style={styles.subtitle}>
                            Your emotionally attuned AI companion for deep, meaningful conversations.
                        </Text>
                        <Text style={styles.description}>
                            FirstPerson listens with empathy, understands your emotions, and responds with genuine care.
                        </Text>
                        <Text style={styles.description}>
                            All conversations are private and stored locally on your device.
                        </Text>
                    </View>
                )}

                {/* Step 2: First-Turn Mode Selection */}
                {step === 1 && (
                    <View style={styles.step}>
                        <Text style={styles.title}>How would you like to begin?</Text>
                        <Text style={styles.subtitle}>
                            Choose a mode that resonates with you today.
                        </Text>

                        <View style={styles.modesContainer}>
                            {FIRST_TURN_MODES.map(mode => (
                                <TouchableOpacity
                                    key={mode.id}
                                    onPress={() => handleModeSelect(mode.id)}
                                    style={[
                                        styles.modeCard,
                                        {
                                            borderColor: mode.color,
                                            backgroundColor: selectedMode === mode.id ? `${mode.color}15` : '#f9f9f9',
                                            borderWidth: selectedMode === mode.id ? 2 : 1,
                                        },
                                    ]}
                                >
                                    <Text style={styles.modeIcon}>{mode.icon}</Text>
                                    <Text style={[styles.modeName, { color: mode.color }]}>
                                        {mode.name}
                                    </Text>
                                    <Text style={styles.modeDescription}>
                                        {mode.description}
                                    </Text>
                                </TouchableOpacity>
                            ))}
                        </View>
                    </View>
                )}

                {/* Step 3: Personalization */}
                {step === 2 && (
                    <View style={styles.step}>
                        <Text style={styles.title}>One more thing...</Text>
                        <Text style={styles.subtitle}>
                            What would you like me to call you?
                        </Text>

                        <View style={styles.inputContainer}>
                            {/* Simple text input simulation - in a full app, use TextInput */}
                            <Text style={styles.inputLabel}>Your name (optional)</Text>
                            <Text style={styles.inputHint}>
                                This helps me personalize our conversations.
                            </Text>
                        </View>

                        <View style={styles.privacyNotice}>
                            <Ionicons name="shield-checkmark" size={20} color="#4CAF50" />
                            <Text style={styles.privacyText}>
                                Your data is never shared or used for training.
                            </Text>
                        </View>
                    </View>
                )}
            </ScrollView>

            {/* Action Buttons */}
            <View style={styles.footer}>
                <TouchableOpacity
                    onPress={handleSkip}
                    style={styles.skipButton}
                >
                    <Text style={styles.skipButtonText}>Skip</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    onPress={handleContinue}
                    disabled={step === 1 && !selectedMode}
                    style={[
                        styles.continueButton,
                        step === 1 && !selectedMode && styles.continueButtonDisabled,
                    ]}
                >
                    <Text style={styles.continueButtonText}>
                        {step === 2 ? 'Start Conversation' : 'Continue'}
                    </Text>
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
    },
    scrollView: {
        flex: 1,
    },
    content: {
        flexGrow: 1,
        paddingHorizontal: 20,
        paddingVertical: 20,
    },
    step: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    iconLarge: {
        width: 120,
        height: 120,
        borderRadius: 60,
        backgroundColor: '#f0f0f0',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 24,
    },
    iconText: {
        fontSize: 60,
    },
    title: {
        fontSize: 24,
        fontWeight: '700',
        textAlign: 'center',
        color: '#000',
        marginBottom: 12,
    },
    subtitle: {
        fontSize: 16,
        textAlign: 'center',
        color: '#666',
        marginBottom: 16,
        lineHeight: 24,
    },
    description: {
        fontSize: 14,
        textAlign: 'center',
        color: '#999',
        marginVertical: 8,
        lineHeight: 20,
    },
    modesContainer: {
        marginTop: 24,
        gap: 12,
    },
    modeCard: {
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
    },
    modeIcon: {
        fontSize: 32,
        marginBottom: 8,
    },
    modeName: {
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 4,
    },
    modeDescription: {
        fontSize: 12,
        color: '#999',
        textAlign: 'center',
    },
    inputContainer: {
        marginVertical: 20,
    },
    inputLabel: {
        fontSize: 14,
        fontWeight: '600',
        marginBottom: 8,
    },
    inputHint: {
        fontSize: 12,
        color: '#999',
    },
    privacyNotice: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 24,
        padding: 12,
        borderRadius: 8,
        backgroundColor: '#f0f8f4',
        gap: 8,
    },
    privacyText: {
        fontSize: 12,
        color: '#4CAF50',
        flex: 1,
    },
    footer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
    },
    skipButton: {
        paddingHorizontal: 20,
        paddingVertical: 12,
    },
    skipButtonText: {
        fontSize: 14,
        color: '#999',
    },
    continueButton: {
        paddingHorizontal: 32,
        paddingVertical: 12,
        backgroundColor: '#007AFF',
        borderRadius: 8,
    },
    continueButtonDisabled: {
        opacity: 0.5,
    },
    continueButtonText: {
        fontSize: 14,
        fontWeight: '600',
        color: '#fff',
    },
});
