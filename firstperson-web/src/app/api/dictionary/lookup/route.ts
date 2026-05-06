import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = (process.env.BACKEND_URL || 'http://localhost:8000').trim();

export async function GET(request: NextRequest) {
  try {
    const word = (request.nextUrl.searchParams.get('word') || '').trim();
    const sessionKey = (request.nextUrl.searchParams.get('sessionKey') || '').trim();
    const refresh = (request.nextUrl.searchParams.get('refresh') || '').trim();

    if (!word) {
      return NextResponse.json(
        { success: false, error: 'word query parameter is required' },
        { status: 400 }
      );
    }

    const sessionParam = sessionKey
      ? `&session_key=${encodeURIComponent(sessionKey)}`
      : '';
    const refreshParam = refresh === '1' || refresh.toLowerCase() === 'true'
      ? '&refresh=true'
      : '';

    const upstream = await fetch(
      `${BACKEND_URL}/dictionary/lookup?word=${encodeURIComponent(word)}${sessionParam}${refreshParam}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    const data = await upstream.json().catch(() => ({
      success: false,
      error: 'Failed to parse backend response',
    }));

    if (!upstream.ok) {
      return NextResponse.json(
        { success: false, error: data?.error || 'Dictionary lookup failed' },
        { status: upstream.status }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Dictionary lookup proxy error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to connect to backend dictionary service' },
      { status: 500 }
    );
  }
}
