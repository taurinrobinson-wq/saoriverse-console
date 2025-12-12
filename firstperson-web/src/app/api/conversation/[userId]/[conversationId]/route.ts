import { NextResponse, NextRequest } from "next/server";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ userId: string; conversationId: string }> }
) {
  const { userId, conversationId } = await params;

  try {
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
    const response = await fetch(
      `${backendUrl}/conversation/${userId}/${conversationId}`
    );
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Error fetching conversation:", error);
    return NextResponse.json(
      { success: false, error: "Failed to load conversation" },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ userId: string; conversationId: string }> }
) {
  const { userId, conversationId } = await params;

  try {
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
    const response = await fetch(
      `${backendUrl}/conversation/${userId}/${conversationId}`,
      { method: "DELETE" }
    );
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Error deleting conversation:", error);
    return NextResponse.json(
      { success: false, error: "Failed to delete conversation" },
      { status: 500 }
    );
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ userId: string; conversationId: string }> }
) {
  const { userId, conversationId } = await params;
  const body = await request.json();

  try {
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
    const response = await fetch(
      `${backendUrl}/conversation/${userId}/${conversationId}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }
    );
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Error renaming conversation:", error);
    return NextResponse.json(
      { success: false, error: "Failed to rename conversation" },
      { status: 500 }
    );
  }
}
