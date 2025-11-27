import React, { useState } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  Text,
  View,
  TextInput,
  ScrollView,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import HeatmapOverlay from './HeatmapOverlay';
import ReframeButton from './ReframeButton';

/**
 * Mock manipulation detection data
 * In production, this would come from an ML model
 */
const MOCK_MANIPULATIONS = {
  "You're being too sensitive about this.": {
    highlights: [
      { start: 0, end: 26, severity: 'high', type: 'gaslighting' }
    ],
    reframe: "I hear that this is important to you. Let's discuss it."
  },
  "I never said that, you're imagining things.": {
    highlights: [
      { start: 0, end: 14, severity: 'high', type: 'denial' },
      { start: 16, end: 42, severity: 'medium', type: 'gaslighting' }
    ],
    reframe: "Let me clarify what I meant earlier."
  },
  "Everyone agrees with me, you're the only one who doesn't see it.": {
    highlights: [
      { start: 0, end: 22, severity: 'medium', type: 'social_pressure' },
      { start: 24, end: 62, severity: 'high', type: 'isolation' }
    ],
    reframe: "I'd like to understand your perspective better."
  },
  "After everything I've done for you, this is how you treat me?": {
    highlights: [
      { start: 0, end: 30, severity: 'high', type: 'guilt_tripping' },
      { start: 32, end: 59, severity: 'medium', type: 'emotional_manipulation' }
    ],
    reframe: "I feel disappointed. Can we talk about expectations?"
  },
  "If you really loved me, you wouldn't question my decisions.": {
    highlights: [
      { start: 0, end: 21, severity: 'high', type: 'conditional_love' },
      { start: 23, end: 57, severity: 'medium', type: 'control' }
    ],
    reframe: "I value your input even when we disagree."
  }
};

// Sample messages for demonstration
const SAMPLE_MESSAGES = [
  "You're being too sensitive about this.",
  "I never said that, you're imagining things.",
  "Everyone agrees with me, you're the only one who doesn't see it.",
  "After everything I've done for you, this is how you treat me?",
  "If you really loved me, you wouldn't question my decisions.",
];

export default function App() {
  const [inputText, setInputText] = useState('');
  const [analyzedText, setAnalyzedText] = useState('');
  const [highlights, setHighlights] = useState([]);
  const [selectedHighlight, setSelectedHighlight] = useState(null);
  const [reframeSuggestion, setReframeSuggestion] = useState('');
  const [showReframe, setShowReframe] = useState(false);

  /**
   * Analyze text for manipulation patterns
   * Uses mock data - in production would call ML model
   */
  const analyzeText = (text) => {
    setAnalyzedText(text);
    
    // Check if text matches any mock manipulation patterns
    const mockResult = MOCK_MANIPULATIONS[text];
    
    if (mockResult) {
      setHighlights(mockResult.highlights);
      setReframeSuggestion(mockResult.reframe);
    } else {
      // For non-matching text, clear highlights
      setHighlights([]);
      setReframeSuggestion('');
    }
    setShowReframe(false);
    setSelectedHighlight(null);
  };

  /**
   * Handle when a highlighted segment is pressed
   */
  const handleHighlightPress = (highlight) => {
    setSelectedHighlight(highlight);
    setShowReframe(true);
  };

  /**
   * Handle reframe button action
   */
  const handleReframeAction = (suggestion) => {
    if (suggestion) {
      // Apply the reframe - replace analyzed text with suggestion
      setAnalyzedText(suggestion);
      setHighlights([]);
      setReframeSuggestion('');
    }
    setShowReframe(false);
    setSelectedHighlight(null);
  };

  /**
   * Load a sample message for demonstration
   */
  const loadSampleMessage = (message) => {
    setInputText(message);
    analyzeText(message);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        <ScrollView 
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>📩 Message UI Overlay</Text>
            <Text style={styles.subtitle}>Manipulation Detection Prototype</Text>
          </View>

          {/* Input Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Enter Message Text</Text>
            <TextInput
              style={styles.textInput}
              placeholder="Type or paste a message to analyze..."
              placeholderTextColor="#999"
              multiline
              value={inputText}
              onChangeText={setInputText}
            />
            <TouchableOpacity 
              style={styles.analyzeButton}
              onPress={() => analyzeText(inputText)}
              activeOpacity={0.7}
            >
              <Text style={styles.analyzeButtonText}>Analyze Message</Text>
            </TouchableOpacity>
          </View>

          {/* Sample Messages */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Sample Messages</Text>
            <Text style={styles.sectionHint}>Tap to load and analyze</Text>
            <ScrollView 
              horizontal 
              showsHorizontalScrollIndicator={false}
              style={styles.samplesScroll}
            >
              {SAMPLE_MESSAGES.map((message, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.sampleChip}
                  onPress={() => loadSampleMessage(message)}
                  activeOpacity={0.7}
                >
                  <Text style={styles.sampleChipText} numberOfLines={2}>
                    {message.substring(0, 30)}...
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>

          {/* Heatmap Overlay Display */}
          {analyzedText ? (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Analysis Result</Text>
              {highlights.length > 0 && (
                <View style={styles.legendContainer}>
                  <View style={styles.legendItem}>
                    <View style={[styles.legendColor, styles.highSeverityLegend]} />
                    <Text style={styles.legendText}>High</Text>
                  </View>
                  <View style={styles.legendItem}>
                    <View style={[styles.legendColor, styles.mediumSeverityLegend]} />
                    <Text style={styles.legendText}>Medium</Text>
                  </View>
                  <View style={styles.legendItem}>
                    <View style={[styles.legendColor, styles.lowSeverityLegend]} />
                    <Text style={styles.legendText}>Low</Text>
                  </View>
                </View>
              )}
              <HeatmapOverlay
                text={analyzedText}
                highlights={highlights}
                onHighlightPress={handleHighlightPress}
              />
              {highlights.length > 0 && (
                <Text style={styles.tapHint}>
                  Tap highlighted text to see reframe suggestion
                </Text>
              )}
              {highlights.length === 0 && (
                <Text style={styles.noIssuesText}>
                  ✅ No manipulation patterns detected
                </Text>
              )}
            </View>
          ) : null}

          {/* Reframe Button */}
          <ReframeButton
            originalText={selectedHighlight?.type || ''}
            reframeSuggestion={reframeSuggestion}
            onPress={handleReframeAction}
            visible={showReframe && reframeSuggestion}
          />

          {/* Info Section */}
          <View style={styles.infoSection}>
            <Text style={styles.infoTitle}>About This Prototype</Text>
            <Text style={styles.infoText}>
              This prototype demonstrates the core UI components for the Message 
              UI Overlay feature. It uses mock data to simulate manipulation 
              detection and highlights text segments with varying severity levels.
            </Text>
            <Text style={styles.infoText}>
              In the full implementation, an ML classifier would analyze messages 
              in real-time to detect manipulation patterns.
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
    paddingTop: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  sectionHint: {
    fontSize: 14,
    color: '#888',
    marginBottom: 12,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    minHeight: 100,
    textAlignVertical: 'top',
    backgroundColor: '#fafafa',
    color: '#1a1a1a',
  },
  analyzeButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 12,
  },
  analyzeButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  samplesScroll: {
    flexGrow: 0,
  },
  sampleChip: {
    backgroundColor: '#f0f0f0',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 20,
    marginRight: 10,
    maxWidth: 180,
  },
  sampleChipText: {
    fontSize: 13,
    color: '#444',
  },
  legendContainer: {
    flexDirection: 'row',
    marginBottom: 12,
    gap: 16,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  legendColor: {
    width: 16,
    height: 16,
    borderRadius: 4,
  },
  highSeverityLegend: {
    backgroundColor: 'rgba(255, 59, 48, 0.35)',
  },
  mediumSeverityLegend: {
    backgroundColor: 'rgba(255, 149, 0, 0.35)',
  },
  lowSeverityLegend: {
    backgroundColor: 'rgba(255, 204, 0, 0.35)',
  },
  legendText: {
    fontSize: 13,
    color: '#666',
  },
  tapHint: {
    fontSize: 13,
    color: '#007AFF',
    fontStyle: 'italic',
    marginTop: 8,
    textAlign: 'center',
  },
  noIssuesText: {
    fontSize: 15,
    color: '#4caf50',
    marginTop: 8,
    textAlign: 'center',
    fontWeight: '500',
  },
  infoSection: {
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    padding: 16,
    marginTop: 16,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 8,
  },
});
