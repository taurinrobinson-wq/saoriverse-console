#!/usr/bin/env node
// Run an admin-mode insert/upsert against Supabase for quick debugging.
// Requires environment variables:
// SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (service role key)

import { createClient } from '@supabase/supabase-js';
import { randomUUID } from 'crypto';

const SUPABASE_URL = process.env.SUPABASE_URL;
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.PROJECT_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SERVICE_ROLE_KEY) {
    console.error('Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment.');
    console.error('Set env and re-run: SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... node dev_tools/run_admin_upsert.mjs');
    process.exit(2);
}

const admin = createClient(SUPABASE_URL, SERVICE_ROLE_KEY, { auth: { persistSession: false } });

async function run() {
    const userId = process.env.DEBUG_TEST_USER_ID || '00000000-0000-4000-8000-000000000001';
    const conversationId = randomUUID();
    const nowIso = new Date().toISOString();

    console.log('Testing admin insert for user', userId, 'conversation', conversationId);

    // Insert user message
    const { data: d1, error: e1 } = await admin.from('conversation_messages').insert([{
        user_id: userId,
        conversation_id: conversationId,
        role: 'user',
        message: 'Test message from admin script',
        first_name: null,
        timestamp: nowIso
    }]);
    console.log('insert user ->', { data: d1, error: e1 });

    // Insert assistant message
    const { data: d2, error: e2 } = await admin.from('conversation_messages').insert([{
        user_id: userId,
        conversation_id: conversationId,
        role: 'assistant',
        message: 'Test assistant reply',
        timestamp: new Date().toISOString()
    }]);
    console.log('insert assistant ->', { data: d2, error: e2 });

    // Upsert conversation metadata
    const upsertRow = {
        user_id: userId,
        conversation_id: conversationId,
        title: 'Admin test conv',
        first_message: 'Test message from admin script',
        first_response: 'Test assistant reply',
        message_count: 2,
        updated_at: nowIso,
        archived: false,
        emotional_context: {},
        topics: []
    };
    const { data: du, error: eu } = await admin.from('conversations').upsert([upsertRow], { onConflict: 'user_id,conversation_id' }).select();
    console.log('upsert conv ->', { data: du, error: eu });
}

run().then(() => process.exit(0)).catch(err => { console.error('Error running admin upsert:', err); process.exit(1) });
