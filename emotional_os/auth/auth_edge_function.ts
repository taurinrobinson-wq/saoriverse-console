import { createClient } from "npm:@supabase/supabase-js@2.45.4";
import { createHash, pbkdf2Sync, randomBytes } from "node:crypto";

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

// Password hashing functions
function hashPassword(password: string, salt?: string): { hash: string, salt: string } {
  const saltBuffer = salt ? Buffer.from(salt, 'hex') : randomBytes(32);
  const hash = pbkdf2Sync(password, saltBuffer, 100000, 64, 'sha256');

  return {
    hash: hash.toString('hex'),
    salt: saltBuffer.toString('hex')
  };
}

function verifyPassword(password: string, hash: string, salt: string): boolean {
  const { hash: newHash } = hashPassword(password, salt);
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

// Create user account
async function createUser(data: any, admin: any): Promise<any> {
  try {
    console.log("DEBUG: createUser called with data:", JSON.stringify(data, null, 2));

    const { username, password_hash, salt, password, email, first_name, last_name, created_at } = data;

    console.log("DEBUG: Destructured values:", {
      username: typeof username + " - " + username,
      password: typeof password + " - " + (password ? "[REDACTED]" : "null/undefined"),
      email: typeof email + " - " + email,
      first_name: typeof first_name + " - " + first_name,
      last_name: typeof last_name + " - " + last_name,
      created_at: typeof created_at + " - " + created_at
    });

    // If client supplied a raw password, hash it server-side so we always store a hash+salt
    let final_password_hash = password_hash;
    let final_salt = salt;
    if (!final_password_hash && password) {
      const h = hashPassword(password);
      final_password_hash = h.hash;
      final_salt = h.salt;
    }

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

    // Create new user (always include first_name / last_name)
    const insertPayload: any = {
      username,
      password_hash: final_password_hash,
      salt: final_salt,
      email: email || null,
      first_name: first_name || null,
      last_name: last_name || null,
      created_at,
      last_login: null,
      is_active: true
    };

    // Debug: log payload being inserted (helps diagnose missing fields after deploy)
    try { console.log("createUser: insertPayload=", JSON.stringify(insertPayload)); } catch (e) { }

    const { data: newUser, error } = await admin
      .from('users')
      .insert([insertPayload])
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
    const isValidPassword = verifyPassword(password, user.password_hash, user.salt);

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