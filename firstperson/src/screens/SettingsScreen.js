/**
 * SettingsScreen.js
 * 
 * User settings, preferences, transcript management, and privacy controls.
 */

import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    TouchableOpacity,
    StyleSheet,
    SafeAreaView,
    ScrollView,
    Switch,
    Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as StorageService from '../services/StorageService';

export default function SettingsScreen({ navigation }) {
    const [preferences, setPreferences] = useState({});
    const [conversations, setConversations] = useState([]);
    const [stats, setStats] = useState({
        totalMessages: 0,
        totalConversations: 0,
        storageUsed: '0 KB',
    });

    useEffect(() => {
        loadSettings();
    }, []);

    const loadSettings = async () => {
        try {
            const prefs = await StorageService.getUserPreferences();
            setPreferences(prefs);

            const convs = await StorageService.getAllConversations();
            setConversations(convs);

            // Calculate stats
            let totalMessages = 0;
            const allConversations = await Promise.all(
                convs.map(c => StorageService.getConversation(c.id))
            );
            totalMessages = allConversations.reduce((sum, msgs) => sum + msgs.length, 0);

            setStats({
                totalMessages,
                totalConversations: convs.length,
                storageUsed: '~' + Math.round(totalMessages * 0.5) + ' KB',
            });
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    };

    const handleClearData = () => {
        Alert.alert(
            'Clear All Data',
            'This will delete all conversations and preferences. This cannot be undone.',
            [
                { text: 'Cancel', onPress: () => { } },
                {
                    text: 'Clear',
                    onPress: async () => {
                        try {
                            await StorageService.clearAllData();
                            setConversations([]);
                            setStats({ totalMessages: 0, totalConversations: 0, storageUsed: '0 KB' });
                            Alert.alert('Success', 'All data has been cleared');
                        } catch (error) {
                            Alert.alert('Error', 'Could not clear data: ' + String(error));
                        }
                    },
                    style: 'destructive',
                },
            ]
        );
    };

    const handleExportConversation = (conversationId) => {
        Alert.alert(
            'Export Conversation',
            'This feature will be available soon. You can view conversations in the chat screen.'
        );
    };

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView style={styles.scrollView}>
                {/* Statistics Section */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Statistics</Text>
                    <View style={styles.statsGrid}>
                        <View style={styles.statCard}>
                            <Text style={styles.statValue}>{stats.totalConversations}</Text>
                            <Text style={styles.statLabel}>Conversations</Text>
                        </View>
                        <View style={styles.statCard}>
                            <Text style={styles.statValue}>{stats.totalMessages}</Text>
                            <Text style={styles.statLabel}>Messages</Text>
                        </View>
                        <View style={styles.statCard}>
                            <Text style={styles.statValue}>{stats.storageUsed}</Text>
                            <Text style={styles.statLabel}>Storage</Text>
                        </View>
                    </View>
                </View>

                {/* Preferences Section */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Preferences</Text>

                    <View style={styles.preferenceItem}>
                        <View>
                            <Text style={styles.preferenceLabel}>Dark Mode</Text>
                            <Text style={styles.preferenceDescription}>Easier on the eyes</Text>
                        </View>
                        <Switch
                            value={preferences.darkMode || false}
                            onValueChange={(value) => {
                                const updated = { ...preferences, darkMode: value };
                                setPreferences(updated);
                                StorageService.setUserPreferences(updated);
                            }}
                        />
                    </View>

                    <View style={styles.preferenceItem}>
                        <View>
                            <Text style={styles.preferenceLabel}>Notifications</Text>
                            <Text style={styles.preferenceDescription}>Reminders for new conversations</Text>
                        </View>
                        <Switch
                            value={preferences.notifications || false}
                            onValueChange={(value) => {
                                const updated = { ...preferences, notifications: value };
                                setPreferences(updated);
                                StorageService.setUserPreferences(updated);
                            }}
                        />
                    </View>

                    <View style={styles.preferenceItem}>
                        <View>
                            <Text style={styles.preferenceLabel}>Analytics</Text>
                            <Text style={styles.preferenceDescription}>Help improve FirstPerson (anonymous)</Text>
                        </View>
                        <Switch
                            value={preferences.analytics !== false}
                            onValueChange={(value) => {
                                const updated = { ...preferences, analytics: value };
                                setPreferences(updated);
                                StorageService.setUserPreferences(updated);
                            }}
                        />
                    </View>
                </View>

                {/* Conversations Section */}
                {conversations.length > 0 && (
                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>Conversations</Text>
                        {conversations.map(conv => (
                            <View key={conv.id} style={styles.conversationItem}>
                                <View style={styles.conversationInfo}>
                                    <Text style={styles.conversationTitle} numberOfLines={1}>
                                        {conv.title}
                                    </Text>
                                    <Text style={styles.conversationMeta}>
                                        {conv.messageCount} messages • {new Date(conv.timestamp).toLocaleDateString()}
                                    </Text>
                                </View>
                                <TouchableOpacity
                                    onPress={() => handleExportConversation(conv.id)}
                                    style={styles.exportButton}
                                >
                                    <Ionicons name="download" size={18} color="#007AFF" />
                                </TouchableOpacity>
                            </View>
                        ))}
                    </View>
                )}

                {/* Privacy & Security */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Privacy & Security</Text>

                    <View style={styles.infoCard}>
                        <Ionicons name="shield-checkmark" size={20} color="#4CAF50" />
                        <Text style={styles.infoText}>
                            All conversations are stored locally on your device. We never access or upload your data.
                        </Text>
                    </View>

                    <TouchableOpacity style={styles.linkButton}>
                        <Text style={styles.linkButtonText}>Privacy Policy</Text>
                        <Ionicons name="chevron-forward" size={18} color="#007AFF" />
                    </TouchableOpacity>

                    <TouchableOpacity style={styles.linkButton}>
                        <Text style={styles.linkButtonText}>Terms of Service</Text>
                        <Ionicons name="chevron-forward" size={18} color="#007AFF" />
                    </TouchableOpacity>
                </View>

                {/* About Section */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>About</Text>

                    <View style={styles.aboutItem}>
                        <Text style={styles.aboutLabel}>Version</Text>
                        <Text style={styles.aboutValue}>1.0.0</Text>
                    </View>

                    <View style={styles.aboutItem}>
                        <Text style={styles.aboutLabel}>Backend</Text>
                        <Text style={styles.aboutValue}>FastAPI</Text>
                    </View>
                </View>

                {/* Danger Zone */}
                <View style={styles.section}>
                    <TouchableOpacity
                        onPress={handleClearData}
                        style={styles.dangerButton}
                    >
                        <Ionicons name="trash" size={18} color="#FF3B30" />
                        <Text style={styles.dangerButtonText}>Clear All Data</Text>
                    </TouchableOpacity>
                </View>

                <View style={{ height: 20 }} />
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f9f9f9',
    },
    scrollView: {
        flex: 1,
    },
    section: {
        backgroundColor: '#fff',
        marginVertical: 8,
        paddingHorizontal: 16,
        paddingVertical: 12,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: '700',
        marginBottom: 12,
        color: '#000',
    },
    statsGrid: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        gap: 12,
    },
    statCard: {
        flex: 1,
        paddingVertical: 12,
        paddingHorizontal: 8,
        backgroundColor: '#f9f9f9',
        borderRadius: 8,
        alignItems: 'center',
    },
    statValue: {
        fontSize: 20,
        fontWeight: '700',
        color: '#007AFF',
    },
    statLabel: {
        fontSize: 11,
        color: '#666',
        marginTop: 4,
    },
    preferenceItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#f0f0f0',
    },
    preferenceLabel: {
        fontSize: 15,
        fontWeight: '600',
        color: '#000',
    },
    preferenceDescription: {
        fontSize: 12,
        color: '#999',
        marginTop: 2,
    },
    conversationItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#f0f0f0',
    },
    conversationInfo: {
        flex: 1,
        marginRight: 12,
    },
    conversationTitle: {
        fontSize: 14,
        fontWeight: '600',
        color: '#000',
    },
    conversationMeta: {
        fontSize: 11,
        color: '#999',
        marginTop: 2,
    },
    exportButton: {
        padding: 8,
    },
    infoCard: {
        flexDirection: 'row',
        padding: 12,
        backgroundColor: '#f0f8f4',
        borderRadius: 8,
        marginBottom: 12,
        gap: 10,
    },
    infoText: {
        flex: 1,
        fontSize: 12,
        color: '#4CAF50',
        lineHeight: 18,
    },
    linkButton: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#f0f0f0',
    },
    linkButtonText: {
        fontSize: 15,
        color: '#007AFF',
    },
    aboutItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingVertical: 10,
    },
    aboutLabel: {
        fontSize: 14,
        color: '#666',
    },
    aboutValue: {
        fontSize: 14,
        fontWeight: '600',
        color: '#000',
    },
    dangerButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 12,
        borderRadius: 8,
        borderWidth: 1,
        borderColor: '#FF3B30',
        backgroundColor: '#fff',
        gap: 8,
    },
    dangerButtonText: {
        fontSize: 15,
        fontWeight: '600',
        color: '#FF3B30',
    },
});
