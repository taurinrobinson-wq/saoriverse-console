import { NextRequest, NextResponse } from 'next/server';

const SUPABASE_URL = "https://gyqzyuvuuyfjxnramkfq.supabase.co";
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5cXp5dXZ1dXlmanhtYW1rZnEiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTcyODQwNjk2NiwiZXhwIjoyMDQ0Nzgyq2SLCJjb250ZXN0Ijp7ImF1dGhvcml6ZWQiOnRydWUsImhpZ2hfYXNzdXJhbmNlIjpmYWxzZX19.NzU0NjU5NjU3NjUyNjU2NTkyNjk2NTY5NjU2NTY1Ng";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { username, password } = body;

    if (!username || !password) {
      return NextResponse.json(
        { success: false, error: "Username and password are required" },
        { status: 400 }
      );
    }

    // Call Supabase auth-manager edge function
    const response = await fetch(
      `${SUPABASE_URL}/functions/v1/auth-manager`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        },
        body: JSON.stringify({
          action: 'login',
          username,
          password,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { success: false, error: data.error || 'Login failed' },
        { status: response.status }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}
