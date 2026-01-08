export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get("userId");

  if (!userId) {
    return new Response(
      JSON.stringify({ success: false, error: "Missing userId" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  try {
    const backendUrl = (process.env.BACKEND_URL || "http://localhost:8000").trim();
    const response = await fetch(`${backendUrl}/conversations/${userId}`);
    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error fetching conversations:", error);
    return new Response(
      JSON.stringify({
        success: false,
        conversations: [],
        error: "Failed to load conversations",
      }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
