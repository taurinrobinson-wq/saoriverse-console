import React from 'react';
import { TouchableOpacity, Text, StyleSheet, View } from 'react-native';

/**
 * ReframeButton Component
 * 
 * Displays an inline button that offers a reframe suggestion for detected
 * manipulation patterns. Appears near highlighted text.
 * 
 * @param {Object} props
 * @param {string} props.originalText - The original manipulative text
 * @param {string} props.reframeSuggestion - Suggested reframe text
 * @param {Function} props.onPress - Callback when button is pressed
 * @param {boolean} props.visible - Whether the button is visible
 */
const ReframeButton = ({ 
  originalText, 
  reframeSuggestion, 
  onPress, 
  visible = false 
}) => {
  if (!visible) {
    return null;
  }

  return (
    <View style={styles.container}>
      <View style={styles.suggestionBox}>
        <Text style={styles.label}>💡 Suggested Reframe:</Text>
        <Text style={styles.suggestionText}>"{reframeSuggestion}"</Text>
        <View style={styles.buttonRow}>
          <TouchableOpacity 
            style={styles.reframeButton} 
            onPress={() => onPress && onPress(reframeSuggestion)}
            activeOpacity={0.7}
          >
            <Text style={styles.buttonText}>Apply Reframe</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.dismissButton} 
            onPress={() => onPress && onPress(null)}
            activeOpacity={0.7}
          >
            <Text style={styles.dismissButtonText}>Dismiss</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 8,
    paddingHorizontal: 4,
  },
  suggestionBox: {
    backgroundColor: '#e8f5e9',
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#4caf50',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2e7d32',
    marginBottom: 8,
  },
  suggestionText: {
    fontSize: 15,
    color: '#1b5e20',
    fontStyle: 'italic',
    lineHeight: 22,
    marginBottom: 12,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'flex-start',
    gap: 12,
  },
  reframeButton: {
    backgroundColor: '#4caf50',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  dismissButton: {
    backgroundColor: 'transparent',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#9e9e9e',
  },
  dismissButtonText: {
    color: '#757575',
    fontSize: 14,
    fontWeight: '500',
  },
});

export default ReframeButton;
