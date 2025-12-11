"use client";

import { useEffect, useRef } from "react";

interface ResponseDisplayProps {
  text: string;
  audioUrl?: string;
  glyphIntent?: {
    voltage?: string;
    tone?: string;
    certainty?: string;
    energy?: number;
    hesitation?: boolean;
  };
}

export default function ResponseDisplay({
  text,
  audioUrl,
  glyphIntent,
}: ResponseDisplayProps) {
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (audioUrl && audioRef.current) {
      audioRef.current.src = audioUrl;
      audioRef.current.play();
    }
  }, [audioUrl]);

  return (
    <div className="space-y-4">
      <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
        <p className="text-slate-900">{text}</p>
      </div>

      {glyphIntent && (
        <div className="bg-slate-50 p-3 rounded text-xs space-y-1">
          <p className="font-semibold text-slate-700">Emotional Intent:</p>
          {glyphIntent.voltage && (
            <p>
              <span className="text-slate-600">Voltage:</span>{" "}
              <span className="font-mono">{glyphIntent.voltage}</span>
            </p>
          )}
          {glyphIntent.tone && (
            <p>
              <span className="text-slate-600">Tone:</span>{" "}
              <span className="font-mono">{glyphIntent.tone}</span>
            </p>
          )}
          {glyphIntent.certainty && (
            <p>
              <span className="text-slate-600">Certainty:</span>{" "}
              <span className="font-mono">{glyphIntent.certainty}</span>
            </p>
          )}
          {glyphIntent.energy !== undefined && (
            <p>
              <span className="text-slate-600">Energy:</span>{" "}
              <span className="font-mono">{glyphIntent.energy.toFixed(2)}</span>
            </p>
          )}
        </div>
      )}

      {audioUrl && (
        <audio
          ref={audioRef}
          controls
          className="w-full"
          onPlay={() => console.log("Playing audio")}
        />
      )}
    </div>
  );
}
