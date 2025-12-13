import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

// Initialize Supabase client with service role (server-side only)
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL as string,
  process.env.SUPABASE_SERVICE_ROLE_KEY as string
);

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get("user_id");

  if (!userId) {
    return NextResponse.json({ error: "user_id parameter required" }, { status: 400 });
  }

  try {
    const { data, error } = await supabase
      .from("emotion_thresholds")
      .select("emotion, threshold")
      .eq("user_id", userId);

    if (error) {
      console.error("Supabase query error:", error);
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    // Transform array into key-value object
    const thresholds: Record<string, number> = {};
    data?.forEach((row: any) => {
      thresholds[row.emotion] = row.threshold;
    });

    return NextResponse.json(
      {
        success: true,
        user_id: userId,
        thresholds,
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

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { user_id, emotion, threshold } = body;

    if (!user_id || !emotion || threshold === undefined) {
      return NextResponse.json(
        { error: "Missing required fields: user_id, emotion, threshold" },
        { status: 400 }
      );
    }

    const { data, error } = await supabase
      .from("emotion_thresholds")
      .upsert(
        [
          {
            user_id,
            emotion,
            threshold: Math.round(threshold * 100) / 100, // Round to 2 decimals
            updated_at: new Date().toISOString(),
          },
        ],
        { onConflict: "user_id,emotion" }
      )
      .select();

    if (error) {
      console.error("Supabase upsert error:", error);
      return NextResponse.json(
        { error: "Failed to update threshold", details: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json(
      {
        success: true,
        message: "Threshold updated successfully",
        data: data?.[0],
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
