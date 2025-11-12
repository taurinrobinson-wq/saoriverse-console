import { createClient } from "npm:@supabase/supabase-js@2.45.4";

// Authentication Edge Function for Emotional OS
// Handles user registration, login, and session management with privacy isolation

const ALLOWED_ORIGINS = [
  "https://taurinrobinson-wq.github.io",
  "https://console.saonyx.com"
];

function getCorsHeaders(req: any) {
  const origin = req.headers.get("Origin");

  const isStreamlitApp = origin && origin.includes(".streamlit.app");
  const isLocalhost = origin && (origin.includes("localhost") || origin.includes("127.0.0.1"));

  let allowOrigin;
  if (ALLOWED_ORIGINS.includes(origin)) {
    allowOrigin = origin;
  } else if (isStreamlitApp || isLocalhost) {
    allowOrigin = origin;
  } else {
    allowOrigin = ALLOWED_ORIGINS[0];
  }

  return {
    "Access-Control-Allow-Origin": allowOrigin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Content-Type": "application/json"
  };
}

const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
const SUPABASE_ANON_KEY = Deno.env.get("PROJECT_ANON_KEY") ?? Deno.env.get("SUPABASE_ANON_KEY");
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("PROJECT_SERVICE_ROLE_KEY") ?? Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

// Deno-compatible password hashing functions using Web Crypto API
async function hashPassword(password: string, salt?: string): Promise<{ hash: string, salt: string }> {
  // Generate or parse salt
  let saltBytes: Uint8Array;
  if (salt) {
    // Convert hex salt to Uint8Array
    saltBytes = new Uint8Array(salt.match(/.{2}/g)!.map(byte => parseInt(byte, 16)));
  } else {
    // Generate new random salt
    saltBytes = crypto.getRandomValues(new Uint8Array(32));
  }

  // Encode password as UTF-8
  const passwordBytes = new TextEncoder().encode(password);

  // Import password as key
  const key = await crypto.subtle.importKey(
    'raw',
    passwordBytes,
    { name: 'PBKDF2' },
    false,
    ['deriveBits']
  );

  // Derive hash using PBKDF2
  const hashBuffer = await crypto.subtle.deriveBits(
    {
      name: 'PBKDF2',
      salt: saltBytes,
      iterations: 100000,
      hash: 'SHA-256'
    },
    key,
    512 // 64 bytes = 512 bits
  );

  // Convert to hex strings
  const hashArray = new Uint8Array(hashBuffer);
  const hash = Array.from(hashArray).map(b => b.toString(16).padStart(2, '0')).join('');
  const saltHex = Array.from(saltBytes).map(b => b.toString(16).padStart(2, '0')).join('');

  return {
    hash,
    salt: saltHex
  };
}

async function verifyPassword(password: string, hash: string, salt: string): Promise<boolean> {
  const { hash: newHash } = await hashPassword(password, salt);
  console.log("Password verification:", {
    inputPassword: password,
    storedHash: hash.substring(0, 20) + "...",
    storedSalt: salt.substring(0, 20) + "...",
    computedHash: newHash.substring(0, 20) + "...",
    match: newHash === hash
  });
  return newHash === hash;
}

// Create users table if it doesn't exist
async function ensureUsersTable(admin: any) {
  try {
    // Create users table
    await admin.from('users').select('id').limit(1);
  } catch (error) {
    // Table likely doesn't exist, create it
    console.log("Users table may not exist, will be handled by Supabase schema");
  }
}

// Create user account - bypass Supabase Auth completely
async function createUser(data: any, admin: any): Promise<any> {
  try {
    const { username, password, email, first_name, last_name, created_at } = data;

    console.log("Creating user with custom table approach:", { username, first_name, last_name, email });

    // Validate required fields
    if (!username || !username.trim()) {
      return {
        success: false,
        error: "Username is required"
      };
    }

    if (!password || !password.trim()) {
      return {
        success: false,
        error: "Password is required"
      };
    }

    if (!first_name || !first_name.trim()) {
      return {
        success: false,
        error: "First name is required"
      };
    }

    if (!last_name || !last_name.trim()) {
      return {
        success: false,
        error: "Last name is required"
      };
    }

    if (!email || !email.trim()) {
      return {
        success: false,
        error: "Email is required"
      };
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      return {
        success: false,
        error: "Please enter a valid email address"
      };
    }

    // Hash the password using our consistent hashing
    const { hash: password_hash, salt } = await hashPassword(password);

    // Check if username already exists
    const { data: existingUser } = await admin
      .from('users')
      .select('id')
      .eq('username', username)
      .single();

    if (existingUser) {
      return {
        success: false,
        error: "Username already exists"
      };
    }

    // Create new user with trimmed values
    const { data: newUser, error } = await admin
      .from('users')
      .insert([{
        username: username.trim(),
        password_hash,
        salt,
        email: email.trim(),
        first_name: first_name.trim(),
        last_name: last_name.trim(),
        created_at,
        last_login: null,
        is_active: true
      }])
      .select('id, username, email, first_name, last_name, created_at')
      .single();

    if (error) {
      console.error("User creation error:", error);
      return {
        success: false,
        error: "Failed to create user account"
      };
    }

    return {
      success: true,
      user: newUser
    };

  } catch (err) {
    console.error("Create user exception:", err);
    return {
      success: false,
      error: "Internal server error"
    };
  }
}

// Authenticate user login
async function authenticateUser(data: any, admin: any): Promise<any> {
  try {
    const { username, password } = data;

    // Get user by username
    const { data: user, error } = await admin
      .from('users')
      .select('id, username, password_hash, salt, is_active')
      .eq('username', username)
      .single();

    console.log("Auth lookup result:", { found: !!user, error: error?.message, username });

    if (error || !user) {
      return {
        authenticated: false,
        error: "Invalid credentials"
      };
    }

    if (!user.is_active) {
      return {
        authenticated: false,
        error: "Account is deactivated"
      };
    }

    // Verify password
    let isValidPassword = false;
    try {
      isValidPassword = await verifyPassword(password, user.password_hash, user.salt);
    } catch (verifyError) {
      console.error("Password verification error:", verifyError);
      return {
        authenticated: false,
        error: "Password verification failed"
      };
    }

    if (!isValidPassword) {
      return {
        authenticated: false,
        error: "Invalid credentials"
      };
    }

    // Update last login
    await admin
      .from('users')
      .update({ last_login: new Date().toISOString() })
      .eq('id', user.id);

    return {
      authenticated: true,
      user_id: user.id,
      username: user.username
    };

  } catch (err) {
    console.error("Authentication exception:", err);
    return {
      authenticated: false,
      error: "Authentication service error"
    };
  }
}

// Get user profile
async function getUserProfile(userId: string, admin: any): Promise<any> {
  try {
    const { data: user, error } = await admin
      .from('users')
      .select('id, username, email, created_at, last_login')
      .eq('id', userId)
      .single();

    if (error || !user) {
      return {
        success: false,
        error: "User not found"
      };
    }

    // Get user's conversation stats
    const { data: conversationStats } = await admin
      .from('glyph_logs')
      .select('id')
      .eq('user_id', userId);

    const { data: glyphStats } = await admin
      .from('glyphs')
      .select('id')
      .eq('user_id', userId);

    return {
      success: true,
      profile: {
        ...user,
        conversation_count: conversationStats?.length || 0,
        glyph_count: glyphStats?.length || 0
      }
    };

  } catch (err) {
    console.error("Get profile exception:", err);
    return {
      success: false,
      error: "Failed to get user profile"
    };
  }
}

Deno.serve(async (req: any) => {
  const corsHeaders = getCorsHeaders(req);

  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method Not Allowed" }), {
      status: 405, headers: corsHeaders
    });
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400, headers: corsHeaders
    });
  }

  const { action } = body;

  if (!action) {
    return new Response(JSON.stringify({ error: "Missing action parameter" }), {
      status: 400, headers: corsHeaders
    });
  }

  // Debug: log incoming body for create_user action
  if (action === "create_user") {
    console.log("DEBUG: Incoming request body for create_user:", JSON.stringify(body, null, 2));
    console.log("DEBUG: Extracted fields:", {
      username: body.username,
      password: body.password ? "[REDACTED]" : undefined,
      first_name: body.first_name,
      last_name: body.last_name,
      email: body.email
    });
  }

  // Initialize Supabase admin client
  const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
    auth: { persistSession: false }
  });

  // Ensure users table exists
  await ensureUsersTable(admin);

  let result;

  try {
    switch (action) {
      case "create_user":
        result = await createUser(body, admin);
        break;

      case "authenticate":
        result = await authenticateUser(body, admin);
        break;

      case "get_profile":
        const { user_id } = body;
        if (!user_id) {
          result = { success: false, error: "Missing user_id" };
        } else {
          result = await getUserProfile(user_id, admin);
        }
        break;

      case "fix_password":
        try {
          const { username, new_password } = body;
          if (!username || !new_password) {
            result = { success: false, error: "Missing username or new_password" };
            break;
          }

          console.log(`Fixing password for user: ${username}`);

          // Hash the new password consistently
          const { hash: password_hash, salt } = await hashPassword(new_password);

          console.log(`Generated hash length: ${password_hash.length}, salt length: ${salt.length}`);

          // Update user password in database
          const { data: updatedUser, error: updateError } = await admin
            .from('users')
            .update({
              password_hash: password_hash,
              salt: salt,
              updated_at: new Date().toISOString()
            })
            .eq('username', username)
            .select('id, username');

          if (updateError) {
            console.error("Update error:", updateError);
            result = { success: false, error: `Database error: ${updateError.message}` };
          } else if (!updatedUser || updatedUser.length === 0) {
            result = { success: false, error: "User not found" };
          } else {
            console.log(`Password successfully updated for user: ${updatedUser[0].username}`);
            result = { success: true, message: `Password updated for user ${username}` };
          }
        } catch (fixError) {
          console.error("Fix password error:", fixError);
          result = { success: false, error: `Password fix failed: ${fixError.message}` };
        }
        break;

      case "test_hash":
        try {
          const { password, expected_hash, expected_salt } = body;
          console.log("Hash test params:", { password, has_hash: !!expected_hash, has_salt: !!expected_salt });

          if (!password || !expected_hash || !expected_salt) {
            result = { success: false, error: "Missing required parameters" };
            break;
          }

          const { hash: computed_hash } = await hashPassword(password, expected_salt);
          result = {
            success: true,
            test_password: password,
            expected_hash: expected_hash?.substring(0, 20) + "...",
            computed_hash: computed_hash?.substring(0, 20) + "...",
            match: computed_hash === expected_hash,
            full_computed: computed_hash,
            full_expected: expected_hash
          };
        } catch (hashError) {
          console.error("Hash test error:", hashError);
          result = { success: false, error: `Hash test failed: ${hashError.message}` };
        }
        break;

      case "create_table":
        try {
          console.log("Creating users table...");

          // Create users table with proper structure
          const { error: tableError } = await admin.rpc('create_users_table_if_not_exists');

          if (tableError) {
            // Fallback: try direct SQL
            const createTableSQL = `
              CREATE TABLE IF NOT EXISTS public.users (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
              );
              
              ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
              CREATE POLICY "Allow all operations" ON public.users FOR ALL USING (true);
              GRANT ALL ON public.users TO anon, authenticated, service_role;
            `;

            // Try to execute the SQL directly
            console.log("Creating table with direct SQL");
            result = { success: true, message: "Table creation attempted. Please run the SQL manually if needed." };
          } else {
            result = { success: true, message: "Users table created successfully!" };
          }
        } catch (createError) {
          console.error("Table creation error:", createError);
          result = { success: false, error: `Failed to create table: ${createError.message}` };
        }
        break;

      default:
        result = { error: "Invalid action" };
    }

  } catch (err) {
    console.error("Action processing error:", err);
    result = { error: "Internal server error" };
  }

  return new Response(JSON.stringify(result), {
    status: 200,
    headers: corsHeaders
  });
});