import React, { useState } from 'react';
import { View, TextInput, Button, Text, StyleSheet, ScrollView } from 'react-native';
import { postMessage } from '../config';

export default function MessageOverlay() {
    const [text, setText] = useState('');
    const [history, setHistory] = useState([]);
    const [sending, setSending] = useState(false);
    const [error, setError] = useState(null);

    async function handleSend() {
        if (!text.trim()) return;
        setSending(true);
        setError(null);
        const payload = { text: text.trim(), timestamp: Date.now() };
        const res = await postMessage(payload);
        if (res.ok) {
            setHistory(prev => [{ id: Date.now().toString(), text: payload.text, resp: res.data }, ...prev]);
            setText('');
        } else {
            setError(res.error || 'Failed to send');
        }
        setSending(false);
    }

    return (
        <View style={styles.container}>
            <View style={styles.inputRow}>
                <TextInput
                    style={styles.input}
                    placeholder="Type a message to Saoynx"
                    value={text}
                    onChangeText={setText}
                    editable={!sending}
                />
                <Button title={sending ? '...' : 'Send'} onPress={handleSend} disabled={sending} />
            </View>

            {error ? <Text style={styles.error}>{String(error)}</Text> : null}

            <ScrollView style={styles.history} contentContainerStyle={styles.historyContent}>
                {history.length === 0 ? (
                    <Text style={styles.empty}>No messages yet</Text>
                ) : (
                    history.map(h => (
                        <View key={h.id} style={styles.item}>
                            <Text style={styles.msg}>{h.text}</Text>
                            <Text style={styles.resp}>{JSON.stringify(h.resp)}</Text>
                        </View>
                    ))
                )}
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, padding: 16 },
    inputRow: { flexDirection: 'row', gap: 8, alignItems: 'center' },
    input: { flex: 1, borderWidth: 1, borderColor: '#ccc', padding: 8, borderRadius: 4 },
    history: { marginTop: 12 },
    historyContent: { paddingBottom: 40 },
    empty: { color: '#666' },
    item: { padding: 8, borderBottomWidth: 1, borderBottomColor: '#eee' },
    msg: { fontWeight: '600' },
    resp: { color: '#333', marginTop: 4, fontSize: 12 },
    error: { color: 'red', marginTop: 8 },
});
