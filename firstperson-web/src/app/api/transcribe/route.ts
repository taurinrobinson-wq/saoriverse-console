import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = (process.env.BACKEND_URL || 'http://localhost:8000').trim();

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();

    // Forward the audio file to the FastAPI backend, preserving auth/cookies
    const headers: Record<string, string> = {};
    const auth = request.headers.get('authorization');
    const cookie = request.headers.get('cookie');
    if (auth) headers['authorization'] = auth;
    if (cookie) headers['cookie'] = cookie;

    const response = await fetch(`${BACKEND_URL}/transcribe`, {
      method: 'POST',
      body: formData,
      headers,
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { success: false, error: data.detail || 'Transcription failed' },
        { status: response.status }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Transcription error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to connect to transcription service' },
      { status: 500 }
    );
  }
}
