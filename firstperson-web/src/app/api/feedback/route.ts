import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = (process.env.BACKEND_URL || 'http://localhost:8000').trim();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    const auth = request.headers.get('authorization');
    const cookie = request.headers.get('cookie');
    if (auth) headers['authorization'] = auth;
    if (cookie) headers['cookie'] = cookie;

    const response = await fetch(`${BACKEND_URL}/api/feedback`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Feedback proxy error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to forward feedback' },
      { status: 500 }
    );
  }
}
