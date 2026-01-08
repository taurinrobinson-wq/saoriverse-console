import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = (process.env.BACKEND_URL || 'http://localhost:8000').trim();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { text, glyph_intent } = body;

    if (!text) {
      return NextResponse.json(
        { success: false, error: "Text is required" },
        { status: 400 }
      );
    }

    // Forward the synthesis request to the FastAPI backend, preserving auth/cookies
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    const auth = request.headers.get('authorization');
    const cookie = request.headers.get('cookie');
    if (auth) headers['authorization'] = auth;
    if (cookie) headers['cookie'] = cookie;

    const response = await fetch(`${BACKEND_URL}/synthesize`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        text,
        glyph_intent: glyph_intent || null,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { success: false, error: data.detail || 'Synthesis failed' },
        { status: response.status }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Synthesis error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to connect to synthesis service' },
      { status: 500 }
    );
  }
}
