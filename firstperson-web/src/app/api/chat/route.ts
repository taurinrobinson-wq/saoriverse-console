import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = (process.env.BACKEND_URL || 'http://localhost:8000').trim();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, userId, context } = body;

    if (!message) {
      return NextResponse.json(
        { success: false, error: "Message is required" },
        { status: 400 }
      );
    }

    // Log outbound payload for debugging
    try {
      console.log("→ PROXY OUTBOUND /chat payload:", {
        message: message,
        userId: userId,
        context: context,
      });
    } catch (e) {
      // ignore logging errors
    }

    // Call the Python FastAPI backend
    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        userId: userId || 'demo_user',
        context: context || null,
      }),
    });

    const data = await response.json().catch((err) => {
      console.error('Proxy: failed to parse backend JSON', err);
      return null;
    });

    // Log inbound response for debugging
    try {
      console.log('← PROXY INBOUND /chat response:', {
        message: data?.message,
        metadata: data?.metadata,
        success: data?.success,
      });
    } catch (e) {
      // ignore logging errors
    }

    if (!response.ok) {
      return NextResponse.json(
        { success: false, error: data.detail || 'Failed to generate response' },
        { status: response.status }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Chat error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}

