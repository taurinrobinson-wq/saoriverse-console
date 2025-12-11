"use client";

import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { useAudioStore } from "@/lib/store";
import { api } from "@/lib/api";
import { Mic, Square } from "lucide-react";

interface AudioRecorderProps {
  onTranscription: (text: string) => void;
  isLoading?: boolean;
}

export function AudioRecorder({
  onTranscription,
  isLoading = false,
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

      setRecordingStatus("🎤 Recording...");
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstart = () => {
        setIsRecording(true);
      };

      mediaRecorder.onstop = async () => {
        setIsRecording(false);
        setRecordingStatus("🔄 Processing audio...");
        const audioBlob = new Blob(chunksRef.current, { type: "audio/wav" });

        try {
          setRecordingStatus("📝 Transcribing...");
          setIsSending(true);

          const result = await api.transcribe(audioBlob);
          setRecordingStatus(null);
          onTranscription(result.text);
        } catch (error) {
          console.error("Transcription error:", error);
          setRecordingStatus("❌ Transcription failed");
          setTimeout(() => setRecordingStatus(null), 3000);
        } finally {
          setIsSending(false);
        }

        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
    } catch (error) {
      console.error("Recording error:", error);
      setRecordingStatus("❌ Could not access microphone");
      setTimeout(() => setRecordingStatus(null), 3000);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
  };

  return (
    <div className="flex flex-col items-center gap-3">
      <motion.button
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isLoading || isSending}
        className={`px-6 py-3 rounded-lg font-semibold transition flex items-center gap-2 ${
          isRecording
            ? "bg-red-600 hover:bg-red-700"
            : "bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
        } text-white ${(isLoading || isSending) && "opacity-50 cursor-not-allowed"}`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        animate={isRecording ? { scale: [1, 1.05, 1] } : {}}
        transition={isRecording ? { duration: 1, repeat: Infinity } : {}}
      >
        {isRecording ? (
          <>
            <Square className="w-5 h-5" />
            Stop Recording
          </>
        ) : (
          <>
            <Mic className="w-5 h-5" />
            Start Recording
          </>
        )}
      </motion.button>
    </div>
  );
}
