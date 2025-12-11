"use client";

import { useState, useRef } from "react";
import { useAudioStore } from "@/lib/store";
import { transcribe } from "@/lib/api";

interface AudioRecorderProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

export default function AudioRecorder({
  onTranscript,
  disabled = false,
}: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const { setRecordingStatus } = useAudioStore();

  const startRecording = async () => {
    try {
      setRecordingStatus("🎤 Accessing microphone...");
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      chunksRef.current = [];
      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (event) => {
        chunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        setRecordingStatus("🔄 Transcribing...");
        setIsSending(true);
        try {
          const audioBlob = new Blob(chunksRef.current, { type: "audio/wav" });
          const result = await transcribe(audioBlob);
          onTranscript(result.text);
          setRecordingStatus(null);
        } catch (error) {
          console.error("Transcription error:", error);
          setRecordingStatus("❌ Transcription failed");
          setTimeout(() => setRecordingStatus(null), 2000);
        } finally {
          setIsSending(false);
        }
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      setRecordingStatus("🎙️ Recording...");
    } catch (error) {
      console.error("Microphone access error:", error);
      setRecordingStatus("❌ Microphone access denied");
      setTimeout(() => setRecordingStatus(null), 2000);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="flex justify-center">
      <button
        onClick={isRecording ? stopRecording : startRecording}
        disabled={disabled || isSending}
        className={`px-6 py-3 rounded-lg font-semibold transition flex items-center gap-2 ${
          isRecording
            ? "bg-red-600 text-white hover:bg-red-700"
            : "bg-indigo-600 text-white hover:bg-indigo-700"
        } ${(disabled || isSending) && "opacity-50 cursor-not-allowed"}`}
      >
        {isRecording ? "⏹️ Stop Recording" : "🎤 Start Recording"}
      </button>
    </div>
  );
}
