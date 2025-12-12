"use client";

import React, { useEffect, useRef, useState } from "react";
import * as faceapi from "face-api.js";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL as string,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY as string
);

interface EmotionDetectorProps {
  userId: string;
  conversationContext?: string;
  isActive?: boolean;
}

export const EmotionDetector: React.FC<EmotionDetectorProps> = ({
  userId,
  conversationContext = "default",
  isActive = true,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [emotion, setEmotion] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number | null>(null);
  const [thresholds, setThresholds] = useState<Record<string, number>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const analyzeIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Load face-api models on mount
  useEffect(() => {
    const loadModels = async () => {
      try {
        setIsLoading(true);
        const modelsPath = "/models";
        await Promise.all([
          faceapi.nets.tinyFaceDetector.loadFromUri(modelsPath),
          faceapi.nets.faceExpressionNet.loadFromUri(modelsPath),
        ]);
        setIsLoading(false);
      } catch (err) {
        setError("Failed to load face detection models. Ensure models are in /public/models");
        console.error("Model loading error:", err);
        setIsLoading(false);
      }
    };

    loadModels();
  }, []);

  // Subscribe to threshold updates in Supabase (Realtime)
  useEffect(() => {
    if (!isActive) return;

    const channel = supabase
      .channel(`emotion-thresholds-${userId}`)
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "emotion_thresholds",
          filter: `user_id=eq.${userId}`,
        },
        (payload) => {
          const row = payload.new as any;
          if (row) {
            setThresholds((prev) => ({
              ...prev,
              [row.emotion]: row.threshold,
            }));
            console.log(`[Emotion] Threshold updated for ${row.emotion}: ${row.threshold}`);
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [userId, isActive]);

  // Initialize webcam
  useEffect(() => {
    if (!isActive || isLoading) return;

    const startWebcam = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 320 }, height: { ideal: 240 } },
          audio: false, // Privacy: audio capture is intentionally disabled
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        setError("Unable to access webcam. Check browser permissions.");
        console.error("Webcam error:", err);
      }
    };

    startWebcam();

    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, [isActive, isLoading]);

  // Analyze video frames for emotion detection
  const analyzeFrame = async () => {
    if (!videoRef.current || !videoRef.current.srcObject) return;

    try {
      const detections = await faceapi
        .detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions())
        .withFaceExpressions();

      if (detections && detections.expressions) {
        const expressions = detections.expressions;
        // Find emotion with highest confidence
        const topEmotion = Object.entries(expressions).reduce((a, b) =>
          a[1] > b[1] ? a : b
        )[0];
        const conf = expressions[topEmotion as keyof typeof expressions];

        // Apply user-specific threshold (default 0.5)
        const threshold = thresholds[topEmotion] ?? 0.5;

        if (conf >= threshold) {
          setEmotion(topEmotion);
          setConfidence(conf);

          // Send only metadata packet to backend (NO video/images)
          const payload = {
            emotion: topEmotion,
            confidence: Math.round(conf * 100) / 100, // Round to 2 decimals
            timestamp: new Date().toISOString(),
            user_id: userId,
            conversation_context: conversationContext,
          };

          // Fire and forget - don't block analysis on network
          fetch("/api/emotions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          }).catch((err) => console.error("Failed to send emotion data:", err));
        } else {
          setEmotion(null);
          setConfidence(null);
        }
      } else {
        setEmotion(null);
        setConfidence(null);
      }
    } catch (err) {
      console.error("Analysis error:", err);
    }
  };

  // Start/stop analysis loop
  useEffect(() => {
    if (!isActive || isLoading || error) {
      if (analyzeIntervalRef.current) {
        clearInterval(analyzeIntervalRef.current);
        analyzeIntervalRef.current = null;
      }
      return;
    }

    // Analyze every 1 second (balance between responsiveness and CPU load)
    analyzeIntervalRef.current = setInterval(analyzeFrame, 1000);

    return () => {
      if (analyzeIntervalRef.current) {
        clearInterval(analyzeIntervalRef.current);
      }
    };
  }, [isActive, isLoading, error, thresholds, userId, conversationContext]);

  if (isLoading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <p className="text-gray-600">Loading emotion detection...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-red-50">
        <div className="text-center">
          <p className="text-red-600 font-medium">{error}</p>
          <p className="text-red-500 text-sm mt-2">Emotion detection unavailable</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full bg-black rounded-lg overflow-hidden">
      {/* Video element (no stream output) */}
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="w-full h-full object-cover"
        style={{ transform: "scaleX(-1)" }} // Mirror video for user comfort
      />

      {/* Hidden canvas for analysis (privacy: not displayed) */}
      <canvas ref={canvasRef} style={{ display: "none" }} />

      {/* Emotion display overlay */}
      {emotion && confidence !== null && (
        <div className="absolute bottom-4 left-4 right-4 bg-black/70 text-white p-3 rounded-lg">
          <p className="text-lg font-bold capitalize">{emotion}</p>
          <p className="text-sm text-gray-300">Confidence: {(confidence * 100).toFixed(0)}%</p>
        </div>
      )}

      {/* Privacy notice */}
      <div className="absolute top-2 left-2 text-xs text-green-400 bg-black/50 px-2 py-1 rounded">
        ✓ Privacy: Video stays local, metadata only
      </div>
    </div>
  );
};

export default EmotionDetector;
