/**
 * MultimodalAffectDisplay.js
 * 
 * Visual display of multimodal affect detection (voice, facial, text).
 * Shows emotional states detected from multiple modalities with confidence scores.
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Pressable } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';

export default function MultimodalAffectDisplay({ affect, theme = 'light' }) {
    const [expandedModality, setExpandedModality] = useState(null);

    if (!affect) return null;

    const themeColors = theme === 'dark'
        ? {
            bg: '#2a2a2a',
            border: '#444',
            text: '#e0e0e0',
            accent: '#64B5F6',
            voiceBg: '#1a3a3a',
            facialBg: '#3a1a2a',
            textBg: '#3a3a1a',
        }
        : {
            bg: '#f5f5f5',
            border: '#e0e0e0',
            text: '#333',
            accent: '#2196F3',
            voiceBg: '#e3f2fd',
            facialBg: '#fce4ec',
            textBg: '#fffde7',
        };

    const getEmotionIcon = (emotion) => {
        const emotionIcons = {
            calm: '😌',
            energetic: '⚡',
            happy: '😊',
            sad: '😢',
            angry: '😠',
            fearful: '😨',
            surprised: '😮',
            disgusted: '🤢',
            neutral: '😐',
            anxious: '😰',
            excited: '🤩',
            confident: '💪',
        };
        return emotionIcons[emotion] || '😊';
    };

    const getConfidenceColor = (confidence) => {
        if (confidence >= 0.8) return '#4CAF50';
        if (confidence >= 0.6) return '#FFC107';
        return '#FF9800';
    };

    const renderConfidenceBar = (value, width = 120) => {
        const percentage = Math.round(value * 100);
        return (
            <View style={{ width, height: 4, backgroundColor: '#ddd', borderRadius: 2, overflow: 'hidden' }}>
                <View
                    style={{
                        width: `${percentage}%`,
                        height: '100%',
                        backgroundColor: getConfidenceColor(value),
                    }}
                />
            </View>
        );
    };

    // Voice affect section
    const renderVoiceAffect = () => {
        if (!affect.voice) return null;

        const isExpanded = expandedModality === 'voice';

        return (
            <Pressable
                onPress={() => setExpandedModality(isExpanded ? null : 'voice')}
                style={({ pressed }) => [
                    styles.modalityCard,
                    { backgroundColor: themeColors.voiceBg, opacity: pressed ? 0.7 : 1 },
                ]}
            >
                <View style={styles.modalityHeader}>
                    <View style={styles.modalityTitle}>
                        <MaterialCommunityIcons
                            name="waveform"
                            size={20}
                            color={themeColors.accent}
                        />
                        <Text style={[styles.modalityLabel, { color: themeColors.text }]}>
                            Voice Affect
                        </Text>
                    </View>
                    <Ionicons
                        name={isExpanded ? 'chevron-up' : 'chevron-down'}
                        size={20}
                        color={themeColors.accent}
                    />
                </View>

                {isExpanded && (
                    <View style={styles.modalityContent}>
                        <View style={styles.emotionRow}>
                            <Text style={[styles.emotionLabel, { color: themeColors.text }]}>
                                {getEmotionIcon(affect.voice.tone)} {affect.voice.tone}
                            </Text>
                            {renderConfidenceBar(affect.voice.confidence)}
                            <Text style={[styles.confidenceText, { color: themeColors.text }]}>
                                {Math.round(affect.voice.confidence * 100)}%
                            </Text>
                        </View>

                        {affect.voice.arousal !== undefined && (
                            <View style={styles.dimensionRow}>
                                <Text style={[styles.dimensionLabel, { color: themeColors.text }]}>
                                    Energy (Arousal)
                                </Text>
                                {renderConfidenceBar(affect.voice.arousal, 100)}
                            </View>
                        )}

                        {affect.voice.valence !== undefined && (
                            <View style={styles.dimensionRow}>
                                <Text style={[styles.dimensionLabel, { color: themeColors.text }]}>
                                    Mood (Valence)
                                </Text>
                                {renderConfidenceBar(affect.voice.valence, 100)}
                            </View>
                        )}

                        {affect.voice.stress_indicator !== undefined && (
                            <View style={styles.dimensionRow}>
                                <Text style={[styles.dimensionLabel, { color: themeColors.text }]}>
                                    Stress Level
                                </Text>
                                {renderConfidenceBar(affect.voice.stress_indicator, 100)}
                            </View>
                        )}

                        {affect.voice.raw_features && (
                            <View style={styles.featuresGrid}>
                                <View style={styles.featureCell}>
                                    <Text style={[styles.featureLabel, { color: themeColors.text }]}>
                                        Pitch
                                    </Text>
                                    <Text style={[styles.featureValue, { color: themeColors.accent }]}>
                                        {affect.voice.raw_features.fundamental_frequency?.toFixed(0)} Hz
                                    </Text>
                                </View>
                                <View style={styles.featureCell}>
                                    <Text style={[styles.featureLabel, { color: themeColors.text }]}>
                                        Speed
                                    </Text>
                                    <Text style={[styles.featureValue, { color: themeColors.accent }]}>
                                        {affect.voice.raw_features.speech_rate?.toFixed(0)} wpm
                                    </Text>
                                </View>
                                <View style={styles.featureCell}>
                                    <Text style={[styles.featureLabel, { color: themeColors.text }]}>
                                        Intensity
                                    </Text>
                                    <Text style={[styles.featureValue, { color: themeColors.accent }]}>
                                        {affect.voice.raw_features.intensity?.toFixed(1)} dB
                                    </Text>
                                </View>
                                <View style={styles.featureCell}>
                                    <Text style={[styles.featureLabel, { color: themeColors.text }]}>
                                        Pauses
                                    </Text>
                                    <Text style={[styles.featureValue, { color: themeColors.accent }]}>
                                        {affect.voice.raw_features.pause_frequency || 0}
                                    </Text>
                                </View>
                            </View>
                        )}
                    </View>
                )}
            </Pressable>
        );
    };

    // Facial expression section
    const renderFacialAffect = () => {
        if (!affect.facial) return null;

        const isExpanded = expandedModality === 'facial';

        return (
            <Pressable
                onPress={() => setExpandedModality(isExpanded ? null : 'facial')}
                style={({ pressed }) => [
                    styles.modalityCard,
                    { backgroundColor: themeColors.facialBg, opacity: pressed ? 0.7 : 1 },
                ]}
            >
                <View style={styles.modalityHeader}>
                    <View style={styles.modalityTitle}>
                        <MaterialCommunityIcons
                            name="face-recognition"
                            size={20}
                            color="#E91E63"
                        />
                        <Text style={[styles.modalityLabel, { color: themeColors.text }]}>
                            Facial Expression
                        </Text>
                    </View>
                    <Ionicons
                        name={isExpanded ? 'chevron-up' : 'chevron-down'}
                        size={20}
                        color="#E91E63"
                    />
                </View>

                {isExpanded && (
                    <View style={styles.modalityContent}>
                        <View style={styles.emotionRow}>
                            <Text style={[styles.emotionLabel, { color: themeColors.text }]}>
                                {getEmotionIcon(affect.facial.emotion)} {affect.facial.emotion}
                            </Text>
                            {renderConfidenceBar(affect.facial.confidence)}
                            <Text style={[styles.confidenceText, { color: themeColors.text }]}>
                                {Math.round(affect.facial.confidence * 100)}%
                            </Text>
                        </View>

                        {affect.facial.au_activations && Object.keys(affect.facial.au_activations).length > 0 && (
                            <View style={styles.ausContainer}>
                                <Text style={[styles.ausLabel, { color: themeColors.text }]}>
                                    Active Action Units
                                </Text>
                                <View style={styles.ausList}>
                                    {Object.entries(affect.facial.au_activations).slice(0, 6).map(([au, intensity]) => (
                                        <View key={au} style={[styles.auBadge, { backgroundColor: getConfidenceColor(intensity) }]}>
                                            <Text style={styles.auText}>{au}</Text>
                                        </View>
                                    ))}
                                </View>
                            </View>
                        )}

                        {affect.facial.arousal !== undefined && (
                            <View style={styles.dimensionRow}>
                                <Text style={[styles.dimensionLabel, { color: themeColors.text }]}>
                                    Arousal
                                </Text>
                                {renderConfidenceBar(affect.facial.arousal, 100)}
                            </View>
                        )}

                        {affect.facial.valence !== undefined && (
                            <View style={styles.dimensionRow}>
                                <Text style={[styles.dimensionLabel, { color: themeColors.text }]}>
                                    Valence
                                </Text>
                                {renderConfidenceBar(affect.facial.valence, 100)}
                            </View>
                        )}

                        {affect.facial.authenticity !== undefined && (
                            <View style={styles.dimensionRow}>
                                <Text style={[styles.dimensionLabel, { color: themeColors.text }]}>
                                    Authenticity
                                </Text>
                                {renderConfidenceBar(affect.facial.authenticity, 100)}
                            </View>
                        )}
                    </View>
                )}
            </Pressable>
        );
    };

    // Text analysis section
    const renderTextAnalysis = () => {
        if (!affect.text) return null;

        const isExpanded = expandedModality === 'text';

        return (
            <Pressable
                onPress={() => setExpandedModality(isExpanded ? null : 'text')}
                style={({ pressed }) => [
                    styles.modalityCard,
                    { backgroundColor: themeColors.textBg, opacity: pressed ? 0.7 : 1 },
                ]}
            >
                <View style={styles.modalityHeader}>
                    <View style={styles.modalityTitle}>
                        <MaterialCommunityIcons
                            name="text-box"
                            size={20}
                            color="#FBC02D"
                        />
                        <Text style={[styles.modalityLabel, { color: themeColors.text }]}>
                            Text Analysis
                        </Text>
                    </View>
                    <Ionicons
                        name={isExpanded ? 'chevron-up' : 'chevron-down'}
                        size={20}
                        color="#FBC02D"
                    />
                </View>

                {isExpanded && (
                    <View style={styles.modalityContent}>
                        <View style={styles.emotionRow}>
                            <Text style={[styles.emotionLabel, { color: themeColors.text }]}>
                                {getEmotionIcon(affect.text.detected_emotion)} {affect.text.detected_emotion}
                            </Text>
                            {renderConfidenceBar(affect.text.confidence)}
                            <Text style={[styles.confidenceText, { color: themeColors.text }]}>
                                {Math.round(affect.text.confidence * 100)}%
                            </Text>
                        </View>

                        {affect.text.sentiment && (
                            <View style={styles.sentimentRow}>
                                <Text style={[styles.dimensionLabel, { color: themeColors.text }]}>
                                    Sentiment
                                </Text>
                                <Text style={[styles.sentimentLabel, { color: themeColors.accent }]}>
                                    {affect.text.sentiment > 0 ? '📈 Positive' : affect.text.sentiment < 0 ? '📉 Negative' : '😐 Neutral'}
                                </Text>
                            </View>
                        )}

                        {affect.text.keywords && affect.text.keywords.length > 0 && (
                            <View style={styles.keywordsContainer}>
                                <Text style={[styles.keywordsLabel, { color: themeColors.text }]}>
                                    Keywords
                                </Text>
                                <View style={styles.keywordsList}>
                                    {affect.text.keywords.slice(0, 5).map((keyword, i) => (
                                        <Text
                                            key={i}
                                            style={[styles.keyword, {
                                                backgroundColor: themeColors.accent,
                                                opacity: 0.2,
                                            }]}
                                        >
                                            {keyword}
                                        </Text>
                                    ))}
                                </View>
                            </View>
                        )}
                    </View>
                )}
            </Pressable>
        );
    };

    // Multimodal fusion
    const renderFusion = () => {
        if (!affect.fusion) return null;

        return (
            <View style={[styles.fusionCard, { backgroundColor: themeColors.bg, borderColor: themeColors.border }]}>
                <Text style={[styles.fusionTitle, { color: themeColors.text }]}>
                    🎯 Integrated Affect
                </Text>

                <View style={styles.fusionEmotionRow}>
                    <Text style={[styles.emotionLabel, { color: themeColors.text }]}>
                        {getEmotionIcon(affect.fusion.integrated_emotion)} {affect.fusion.integrated_emotion}
                    </Text>
                    {renderConfidenceBar(affect.fusion.confidence, 150)}
                    <Text style={[styles.confidenceText, { color: themeColors.text }]}>
                        {Math.round(affect.fusion.confidence * 100)}%
                    </Text>
                </View>

                {affect.fusion.modality_agreement && (
                    <View style={styles.agreementContainer}>
                        <Text style={[styles.agreementLabel, { color: themeColors.text }]}>
                            Modality Alignment: {Math.round(affect.fusion.modality_agreement * 100)}%
                        </Text>
                        {affect.fusion.modality_agreement < 0.6 && (
                            <Text style={[styles.warningText, { color: '#FF6B6B' }]}>
                                ⚠️ Mixed signals detected (e.g., positive words, negative tone)
                            </Text>
                        )}
                    </View>
                )}

                {affect.fusion.dominant_modalities && (
                    <View style={styles.modalitiesContainer}>
                        <Text style={[styles.modalitiesLabel, { color: themeColors.text }]}>
                            Confidence by modality:
                        </Text>
                        {affect.fusion.dominant_modalities.map((mod, i) => (
                            <View key={i} style={styles.modalityConfidence}>
                                <Text style={[styles.modLabel, { color: themeColors.text }]}>
                                    {mod.modality}
                                </Text>
                                {renderConfidenceBar(mod.confidence, 100)}
                            </View>
                        ))}
                    </View>
                )}
            </View>
        );
    };

    return (
        <ScrollView style={[styles.container, { backgroundColor: themeColors.bg }]}>
            <View style={styles.header}>
                <MaterialCommunityIcons
                    name="radar"
                    size={24}
                    color={themeColors.accent}
                />
                <Text style={[styles.headerText, { color: themeColors.text }]}>
                    Multimodal Affect Detection
                </Text>
            </View>

            {affect.fusion && renderFusion()}

            <View style={styles.modalitiesSection}>
                <Text style={[styles.sectionTitle, { color: themeColors.text }]}>
                    Individual Modalities
                </Text>
                {renderVoiceAffect()}
                {renderFacialAffect()}
                {renderTextAnalysis()}
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 12,
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 16,
        gap: 8,
    },
    headerText: {
        fontSize: 16,
        fontWeight: '600',
    },
    sectionTitle: {
        fontSize: 14,
        fontWeight: '600',
        marginBottom: 12,
        marginTop: 8,
    },
    modalitiesSection: {
        marginTop: 8,
    },
    modalityCard: {
        borderRadius: 8,
        padding: 12,
        marginBottom: 12,
        borderWidth: 1,
        borderColor: 'rgba(0,0,0,0.05)',
    },
    modalityHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    modalityTitle: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
    },
    modalityLabel: {
        fontSize: 14,
        fontWeight: '600',
    },
    modalityContent: {
        marginTop: 12,
        paddingTop: 12,
        borderTopWidth: 1,
        borderTopColor: 'rgba(0,0,0,0.1)',
    },
    emotionRow: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
        marginBottom: 12,
    },
    emotionLabel: {
        fontSize: 14,
        fontWeight: '500',
        minWidth: 100,
    },
    confidenceText: {
        fontSize: 12,
        fontWeight: '600',
        marginLeft: 4,
    },
    dimensionRow: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 8,
        paddingHorizontal: 4,
    },
    dimensionLabel: {
        fontSize: 12,
        fontWeight: '500',
    },
    featuresGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
        marginTop: 12,
    },
    featureCell: {
        flex: 1,
        minWidth: '48%',
        padding: 8,
        backgroundColor: 'rgba(0,0,0,0.03)',
        borderRadius: 6,
    },
    featureLabel: {
        fontSize: 11,
        fontWeight: '600',
        marginBottom: 4,
    },
    featureValue: {
        fontSize: 13,
        fontWeight: 'bold',
    },
    ausContainer: {
        marginVertical: 12,
    },
    ausLabel: {
        fontSize: 12,
        fontWeight: '600',
        marginBottom: 6,
    },
    ausList: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 6,
    },
    auBadge: {
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 12,
    },
    auText: {
        color: '#fff',
        fontSize: 11,
        fontWeight: 'bold',
    },
    sentimentRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 8,
        paddingHorizontal: 4,
    },
    sentimentLabel: {
        fontSize: 12,
        fontWeight: '600',
    },
    keywordsContainer: {
        marginTop: 12,
    },
    keywordsLabel: {
        fontSize: 12,
        fontWeight: '600',
        marginBottom: 6,
    },
    keywordsList: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 6,
    },
    keyword: {
        paddingHorizontal: 10,
        paddingVertical: 4,
        borderRadius: 12,
        fontSize: 11,
    },
    fusionCard: {
        borderRadius: 10,
        padding: 14,
        marginBottom: 16,
        borderWidth: 2,
        borderColor: 'rgba(33, 150, 243, 0.3)',
    },
    fusionTitle: {
        fontSize: 15,
        fontWeight: 'bold',
        marginBottom: 12,
    },
    fusionEmotionRow: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
        marginBottom: 12,
    },
    agreementContainer: {
        paddingVertical: 8,
        paddingHorizontal: 8,
        backgroundColor: 'rgba(0,0,0,0.02)',
        borderRadius: 6,
        marginBottom: 10,
    },
    agreementLabel: {
        fontSize: 12,
        fontWeight: '600',
        marginBottom: 4,
    },
    warningText: {
        fontSize: 11,
        marginTop: 4,
    },
    modalitiesContainer: {
        paddingHorizontal: 4,
    },
    modalitiesLabel: {
        fontSize: 12,
        fontWeight: '600',
        marginBottom: 8,
    },
    modalityConfidence: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 6,
    },
    modLabel: {
        fontSize: 11,
        fontWeight: '500',
        minWidth: 80,
    },
});
