import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://gyqzyuvuuyfjxnramkfq.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5cXp5dXZ1dXlmanhucmFta2ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0NjcyMDAsImV4cCI6MjA3MTA0MzIwMH0.4SpC34q7lcURBX4hujkTGqICdSM6ZWASCENnRs5rkS8'; // Use service role key only on backend

export const supabase = createClient(supabaseUrl, supabaseKey);
// Note: For security reasons, avoid exposing the service role key in frontend code. Use it only in secure backend environments.
// For frontend applications, consider using anon keys with appropriate RLS policies.
// Example of creating a client with an anon key (uncomment and replace with your anon key):
// const supabaseAnonKey = 'your-anon-key-here';
// export const supabase = createClient(supabaseUrl, supabaseAnonKey);          
// Ensure to set up Row Level Security (RLS) policies in your Supabase project for secure data access.
// For more information, refer to the Supabase documentation: https://supabase.com/docs/guides/auth#service-role-key
// and https://supabase.com/docs/guides/auth#anon-key
// and https://supabase.com/docs/guides/auth#anon-key

// Example function to fetch data from a table (replace 'your_table' with your actual table name)
export async function fetchData() {
 const { data, error } = await supabase.from('glyphs').select('*');
    if (error) {



    console.error('Error fetching data:', error);
    return null;
    }
    return data;
}







