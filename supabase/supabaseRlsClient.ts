import { createClient } from '@supabase/supabase-js';

function getEnv() {
    // Works both in Deno (Edge Functions) and Node (server)
    if (typeof Deno !== 'undefined' && (Deno as any).env) {
        return {
            SUPABASE_URL: Deno.env.get('SUPABASE_URL') || '',
            SUPABASE_ANON_KEY: Deno.env.get('PROJECT_ANON_KEY') || Deno.env.get('SUPABASE_ANON_KEY') || ''
        };
    }
    return {
        SUPABASE_URL: process.env.SUPABASE_URL || '',
        SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY || ''
    };
}

/**
 * Create an RLS-aware Supabase client using the provided access token.
 * This client should be used for server endpoints that want RLS to apply
 * (i.e., perform DB ops on behalf of the authenticated user).
 */
export function supabaseRlsClient(accessToken: string) {
    const { SUPABASE_URL, SUPABASE_ANON_KEY } = getEnv();
    if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
        throw new Error('Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment');
    }
    return createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
        global: {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        },
        auth: { persistSession: false }
    });
}
