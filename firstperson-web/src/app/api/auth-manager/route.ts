import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { firstName, lastName, email, username, password } = body;

    // Mock registration - in production this calls auth-manager edge function
    if (firstName && lastName && email && username && password) {
      return NextResponse.json(
        { success: true, message: "Registration successful" },
        { status: 200 }
      );
    }

    return NextResponse.json(
      { error: "Missing required fields" },
      { status: 400 }
    );
  } catch (error) {
    return NextResponse.json(
      { error: "Registration failed" },
      { status: 500 }
    );
  }
}
