import React from 'react';
import { StyleSheet, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import MessageOverlay from './src/screens/MessageOverlay';

export default function App() {
  return (
    <View style={styles.container}>
      <MessageOverlay />
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});
