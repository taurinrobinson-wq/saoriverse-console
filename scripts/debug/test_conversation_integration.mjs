/*
Integration test for conversation persistence.

Prereqs:
  npm install @supabase/supabase-js

Environment variables required:
  SUPABASE_URL
  SUPABASE_SERVICE_ROLE_KEY
  SUPABASE_ANON_KEY
  TEST_USER_ACCESS_TOKEN        # JWT for the test user (session.access_token)
  TEST_USER_ID                  # UUID of the test user (auth.uid())

Optional (for negative RLS test):
  OTHER_USER_ACCESS_TOKEN

Run in staging (example):
  npm install @supabase/supabase-js
  node ./scripts/test_conversation_integration.mjs
*/

import { createClient } from '@supabase/supabase-js';

function exitWith(msg, code = 1) {
    console.error(msg);
    process.exit(code);
}

async function main() {
    const SUPABASE_URL = process.env.SUPABASE_URL;
    const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
    const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY;
    const TEST_USER_ACCESS_TOKEN = process.env.TEST_USER_ACCESS_TOKEN;
    const TEST_USER_ID = process.env.TEST_USER_ID;
    const OTHER_USER_ACCESS_TOKEN = process.env.OTHER_USER_ACCESS_TOKEN || null;

    if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY || !SUPABASE_ANON_KEY || !TEST_USER_ACCESS_TOKEN || !TEST_USER_ID) {
        exitWith('Missing required environment variables. See header of this script for required vars.');
    }

    const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, { auth: { persistSession: false } });
    const userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, { global: { headers: { Authorization: `Bearer ${TEST_USER_ACCESS_TOKEN}` } } });
    let otherClient = null;
    if (OTHER_USER_ACCESS_TOKEN) {
        otherClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, { global: { headers: { Authorization: `Bearer ${OTHER_USER_ACCESS_TOKEN}` } } });
    }

    const conversationId = process.env.CONVERSATION_ID || (typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : `conv-${Date.now()}`);
    const userMessage = 'Integration test: hello from test user';
    const assistantReply = 'Integration test: assistant reply';
    const nowIso = new Date().toISOString();

    console.log('Using conversation_id:', conversationId);

    // Insert user message as admin (simulate edge function behavior)
    try {
        const { error: e1 } = await admin.from('conversation_messages').insert([{
            user_id: TEST_USER_ID,
            conversation_id: conversationId,
            role: 'user',
            message: userMessage,
            first_name: 'Testy',
            timestamp: nowIso
        }]);
        if (e1) throw e1;
        console.log('Inserted user message');
    } catch (err) {
        exitWith('Failed to insert user message: ' + err.message || err);
    }

    // Insert assistant reply
    try {
        const { error: e2 } = await admin.from('conversation_messages').insert([{
            user_id: TEST_USER_ID,
            conversation_id: conversationId,
            role: 'assistant',
            message: assistantReply,
            timestamp: new Date().toISOString()
        }]);
        if (e2) throw e2;
        console.log('Inserted assistant message');
    } catch (err) {
        exitWith('Failed to insert assistant message: ' + err.message || err);
    }

    // Upsert conversation metadata
    try {
        const upsertRow = {
            user_id: TEST_USER_ID,
            conversation_id: conversationId,
            title: 'Integration test convo',
            first_message: userMessage,
            first_response: assistantReply,
            message_count: 2,
            updated_at: nowIso,
            archived: false,
            emotional_context: {},
            topics: []
        };
        const { error: eu } = await admin.from('conversations').upsert([upsertRow], { onConflict: 'user_id,conversation_id' }).select();
        if (eu) throw eu;
        console.log('Upserted conversation metadata');
    } catch (err) {
        exitWith('Failed to upsert conversation metadata: ' + (err.message || err));
    }

    // Query as admin to validate rows
    try {
        const { data: adminMsgs, error: aerr } = await admin.from('conversation_messages').select('*').eq('conversation_id', conversationId).order('timestamp', { ascending: true });
        if (aerr) throw aerr;
        console.log('Admin sees conversation_messages count =', adminMsgs.length);
        if (!adminMsgs || adminMsgs.length !== 2) exitWith('Expected 2 messages in conversation_messages (admin view)');

        const { data: convRow, error: cerr } = await admin.from('conversations').select('*').eq('conversation_id', conversationId).eq('user_id', TEST_USER_ID).maybeSingle();
        if (cerr) throw cerr;
        if (!convRow) exitWith('Expected a conversations metadata row for the test conversation');
        console.log('Admin sees conversation metadata:', {
            first_message: convRow.first_message,
            first_response: convRow.first_response,
            message_count: convRow.message_count
        });
    } catch (err) {
        exitWith('Admin validation failed: ' + (err.message || err));
    }

    // Query as test user (RLS validation)
    try {
        const { data: userMsgs, error: uerr } = await userClient.from('conversation_messages').select('*').eq('conversation_id', conversationId).order('timestamp', { ascending: true });
        if (uerr) throw uerr;
        console.log('User client sees conversation_messages count =', userMsgs.length);
        if (!userMsgs || userMsgs.length !== 2) exitWith('Expected test user to see 2 messages (RLS check)');
        // ensure linkage
        if (String(userMsgs[0].user_id) !== String(TEST_USER_ID)) exitWith('RLS: message user_id mismatch');
    } catch (err) {
        exitWith('User RLS validation failed: ' + (err.message || err));
    }

    // Optional: ensure other user cannot see (if OTHER_USER_ACCESS_TOKEN provided)
    if (otherClient) {
        try {
            const { data: otherMsgs, error: oerr } = await otherClient.from('conversation_messages').select('*').eq('conversation_id', conversationId);
            if (oerr) throw oerr;
            if (otherMsgs && otherMsgs.length > 0) exitWith('OTHER user unexpectedly saw messages; RLS misconfigured');
            console.log('Other user cannot see messages (RLS negative test passed)');
        } catch (err) {
            exitWith('Other user RLS test failed: ' + (err.message || err));
        }
    }

    // Bonus: Generate a CSV mock row from userMsgs
    try {
        const { data: finalRows } = await admin.from('conversation_messages').select('user_id, first_name, role, timestamp, message').eq('conversation_id', conversationId).order('timestamp', { ascending: true });
        const header = ['UID', 'First Name', 'Role', 'Timestamp', 'Message'];
        console.log('\nCSV Preview:');
        console.log(header.join(','));
        for (const r of finalRows) {
            const line = [r.user_id, (r.first_name || ''), r.role, new Date(r.timestamp).toISOString(), '"' + (String(r.message).replace(/"/g, '""')) + '"'].join(',');
            console.log(line);
        }
    } catch (err) {
        console.warn('CSV preview generation failed:', err.message || err);
    }

    console.log('\nIntegration test completed successfully');
    process.exit(0);
}

main().catch(err => {
    console.error('Unhandled error:', err);
    process.exit(2);
});
