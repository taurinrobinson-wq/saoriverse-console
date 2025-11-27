import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

/**
 * HeatmapOverlay Component
 * 
 * Displays text with highlighted segments based on manipulation detection data.
 * Uses color intensity to indicate manipulation severity (heatmap visualization).
 * 
 * @param {Object} props
 * @param {string} props.text - The message text to display
 * @param {Array} props.highlights - Array of highlight objects with start, end, and severity
 */
const HeatmapOverlay = ({ text, highlights = [], onHighlightPress }) => {
  // If no text provided, return empty
  if (!text) {
    return null;
  }

  // Sort highlights by start position
  const sortedHighlights = [...highlights].sort((a, b) => a.start - b.start);

  // Build text segments with highlighting
  const renderTextWithHighlights = () => {
    const segments = [];
    let currentIndex = 0;

    sortedHighlights.forEach((highlight, highlightIndex) => {
      const { start, end, severity } = highlight;

      // Add non-highlighted text before this highlight
      if (currentIndex < start) {
        segments.push(
          <Text key={`normal-${currentIndex}`} style={styles.normalText}>
            {text.substring(currentIndex, start)}
          </Text>
        );
      }

      // Add highlighted text
      const highlightStyle = getHighlightStyle(severity);
      segments.push(
        <Text
          key={`highlight-${highlightIndex}`}
          style={[styles.highlightedText, highlightStyle]}
          onPress={() => onHighlightPress && onHighlightPress(highlight)}
        >
          {text.substring(start, end)}
        </Text>
      );

      currentIndex = end;
    });

    // Add remaining non-highlighted text
    if (currentIndex < text.length) {
      segments.push(
        <Text key={`normal-end`} style={styles.normalText}>
          {text.substring(currentIndex)}
        </Text>
      );
    }

    return segments;
  };

  return (
    <View style={styles.container}>
      <Text style={styles.textContainer}>
        {sortedHighlights.length > 0 ? renderTextWithHighlights() : text}
      </Text>
    </View>
  );
};

/**
 * Returns style based on manipulation severity level
 * Higher severity = more intense red/orange coloring
 */
const getHighlightStyle = (severity) => {
  switch (severity) {
    case 'high':
      return styles.highSeverity;
    case 'medium':
      return styles.mediumSeverity;
    case 'low':
      return styles.lowSeverity;
    default:
      return styles.lowSeverity;
  }
};

const styles = StyleSheet.create({
  container: {
    padding: 12,
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    marginVertical: 8,
  },
  textContainer: {
    fontSize: 16,
    lineHeight: 24,
    color: '#1a1a1a',
  },
  normalText: {
    color: '#1a1a1a',
  },
  highlightedText: {
    borderRadius: 4,
    paddingHorizontal: 2,
  },
  highSeverity: {
    backgroundColor: 'rgba(255, 59, 48, 0.35)', // Red - high manipulation
    color: '#8b0000',
  },
  mediumSeverity: {
    backgroundColor: 'rgba(255, 149, 0, 0.35)', // Orange - medium manipulation
    color: '#8b4513',
  },
  lowSeverity: {
    backgroundColor: 'rgba(255, 204, 0, 0.35)', // Yellow - low manipulation
    color: '#5d4e00',
  },
});

export default HeatmapOverlay;
