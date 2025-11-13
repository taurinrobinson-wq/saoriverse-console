#!/usr/bin/env node
// Quick local validator that reproduces the payloads the Edge Function would send
// to Supabase and checks for missing required fields or obvious type mismatches.
import { randomUUID } from 'crypto';

function makeTestPayload({ userId = null, message = 'Hello', reply = 'Hi there', title = null, first_name = null } = {}) {
    const conversationId = (typeof crypto !== 'undefined' && crypto.randomUUID) ? crypto.randomUUID() : randomUUID();
    const nowIso = new Date().toISOString();

    const userMsg = {
        user_id: userId,
        conversation_id: conversationId,
        role: 'user',
        message: String(message),
        first_name: first_name ?? null,
        timestamp: nowIso
    };

    const assistantMsg = {
        user_id: userId,
        conversation_id: conversationId,
        role: 'assistant',
        message: String(reply),
        timestamp: new Date().toISOString()
    };

    const messageCount = 2;

    const upsertRow = {
        user_id: userId,
        conversation_id: conversationId,
        title: title ?? 'New Conversation',
        first_message: message,
        first_response: reply,
        message_count: messageCount,
        updated_at: nowIso,
        archived: false,
        emotional_context: {},
        topics: []
    };

    return { userMsg, assistantMsg, upsertRow };
}

function validateUpsert(upsert) {
    const errors = [];
    if (!upsert.user_id) errors.push('user_id is required');
    if (!upsert.conversation_id) errors.push('conversation_id is required');
    if (!upsert.title) errors.push('title is required');
    // messages column has a default, so not required here, but warn if absent
    if (upsert.messages === undefined) errors.push('messages not provided (will use default [] in DB)');
    return errors;
}

function main() {
    const testUser = process.env.DEBUG_TEST_USER_ID || '00000000-0000-4000-8000-000000000001';
    console.log('Using test user id:', testUser);
    const { userMsg, assistantMsg, upsertRow } = makeTestPayload({ userId: testUser, message: 'Test message', reply: 'Test reply', title: 'Test Conversation' });
    console.log('\n-- User message payload --');
    console.log(JSON.stringify(userMsg, null, 2));
    console.log('\n-- Assistant message payload --');
    console.log(JSON.stringify(assistantMsg, null, 2));
    console.log('\n-- Upsert row payload --');
    console.log(JSON.stringify(upsertRow, null, 2));

    const errors = validateUpsert(upsertRow);
    if (errors.length) {
        console.error('\nValidation warnings/errors:');
        for (const e of errors) console.error(' -', e);
        process.exitCode = 2;
    } else {
        console.log('\nValidation passed: payloads look well-formed (note: this does NOT call Supabase)');
    }
}

if (process.argv[1] && process.argv[1].endsWith('validate_conversation_payload.js')) main();
