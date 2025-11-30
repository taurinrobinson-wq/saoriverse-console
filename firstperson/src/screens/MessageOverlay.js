import React, { useState, useRef } from 'react';
import { View, Text, TextInput, Button, ScrollView, StyleSheet } from 'react-native';
import { postMessage } from '../config';

export default function MessageOverlay() {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef(null);

    async function send() {
        if (!input.trim()) return;
        const userMsg = { role: 'user', text: input };
        setMessages((m) => [...m, userMsg]);
        setInput('');
        setLoading(true);
        try {
            const res = await postMessage(userMsg.text);
            const reply = res && res.reply ? res.reply : (res.error ? `Error: ${res.error}` : 'No response');
            setMessages((m) => [...m, { role: 'assistant', text: reply }]);
        } catch (e) {
            setMessages((m) => [...m, { role: 'assistant', text: `Error: ${String(e)}` }]);
        } finally {
            setLoading(false);
            // scroll to bottom after a tick
            setTimeout(() => scrollRef.current && scrollRef.current.scrollToEnd({ animated: true }), 50);
        }
    }

    return (
        <View style={styles.container}>
            <View style={styles.header}><Text style={styles.title}>FirstPerson — Demo</Text></View>
            <ScrollView style={styles.history} ref={scrollRef}>
                {messages.map((m, i) => (
                    <View key={i} style={[styles.bubble, m.role === 'user' ? styles.user : styles.assistant]}>
                        <Text style={styles.bubbleText}>{m.text}</Text>
                    </View>
                ))}
            </ScrollView>
            <View style={styles.inputRow}>
                <TextInput
                    value={input}
                    onChangeText={setInput}
                    placeholder="Type a message"
                    style={styles.input}
                    multiline
                />
                <Button title={loading ? '...' : 'Send'} onPress={send} disabled={loading} />
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, padding: 12, backgroundColor: '#fff' },
    header: { paddingVertical: 8 },
    title: { fontSize: 18, fontWeight: '600' },
    history: { flex: 1, marginVertical: 8 },
    bubble: { marginVertical: 6, padding: 10, borderRadius: 8, maxWidth: '85%' },
    user: { alignSelf: 'flex-end', backgroundColor: '#DCF8C6' },
    assistant: { alignSelf: 'flex-start', backgroundColor: '#F1F0F0' },
    bubbleText: { fontSize: 16 },
    inputRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
    input: { flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 6, padding: 8, minHeight: 40 },
});
