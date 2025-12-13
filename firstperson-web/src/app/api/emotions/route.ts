import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

// Initialize Supabase client with service role (server-side only)
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL as string,
  process.env.SUPABASE_SERVICE_ROLE_KEY as string
);

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { emotion, confidence, timestamp, user_id, conversation_context } = body;

    // Validate required fields
    if (!emotion || confidence === undefined || !user_id) {
      return NextResponse.json(
        { error: "Missing required fields: emotion, confidence, user_id" },
        { status: 400 }
      );
    }

    // Validate confidence is between 0 and 1
    if (typeof confidence !== "number" || confidence < 0 || confidence > 1) {
      return NextResponse.json(
        { error: "Confidence must be a number between 0 and 1" },
        { status: 400 }
      );
    }

    // Insert into emotions_log table
    const { data, error } = await supabase
      .from("emotions_log")
      .insert([
        {
          user_id,
          emotion,
          confidence,
          timestamp: timestamp || new Date().toISOString(),
          conversation_context: conversation_context || "default",
        },
      ])
      .select();

    if (error) {
      console.error("Supabase insert error:", error);
      return NextResponse.json(
        { error: "Failed to save emotion log", details: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json(
      {
        success: true,
        message: "Emotion logged successfully",
        data: data?.[0],
      },
      { status: 201 }
    );
  } catch (err: any) {
    console.error("API error:", err);
    return NextResponse.json(
      { error: "Internal server error", details: err.message },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get("user_id");
  const limit = searchParams.get("limit") || "100";

  if (!userId) {
    return NextResponse.json({ error: "user_id parameter required" }, { status: 400 });
  }

  try {
    const { data, error } = await supabase
      .from("emotions_log")
      .select("*")
      .eq("user_id", userId)
      .order("timestamp", { ascending: false })
      .limit(parseInt(limit));

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json(
      {
        success: true,
        count: data?.length || 0,
        data,
      },
      { status: 200 }
    );
  } catch (err: any) {
    console.error("API error:", err);
    return NextResponse.json(
      { error: "Internal server error", details: err.message },
      { status: 500 }
    );
  }
}
