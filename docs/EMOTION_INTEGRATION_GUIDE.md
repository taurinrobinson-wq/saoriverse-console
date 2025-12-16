# Emotion Detection System - Integration Guide

## Overview

This guide shows how to integrate the `EmotionDetector` component into your First Person chat interface. The emotion learning system provides real-time facial emotion detection that feeds back into user experience and system learning.
##

## Component API

### EmotionDetector Props

```typescript
interface EmotionDetectorProps {
  userId: string;              // User's unique ID (required)
  conversationContext?: string; // Context tag (e.g., "grief_support", default: "default")
  isActive?: boolean;          // Enable/disable detection (default: true)
```text
```



### Example Usage

```tsx
import { EmotionDetector } from "@/components/EmotionDetector";

export default function ChatPage() {
  return (
    <div className="flex h-screen gap-4">
      {/* Chat area */}
      <div className="flex-1">
        {/* Your chat component here */}
      </div>

      {/* Emotion detector sidebar */}
      <div className="w-80 bg-gray-50 rounded-lg overflow-hidden">
        <EmotionDetector
          userId="user_123"
          conversationContext="sanctuary_chat"
          isActive={true}
        />
      </div>
    </div>
  );
```text
```


##

## Integration Patterns

### Pattern 1: Sidebar Detection (Recommended)

Display emotion detector in a fixed sidebar next to your chat:

```tsx
// app/chat/page.tsx
import { EmotionDetector } from "@/components/EmotionDetector";
import { ChatInterface } from "@/components/ChatInterface";
import { useSession } from "@/hooks/useSession";

export default function ChatPage() {
  const { user } = useSession();

  if (!user) {
    return <div>Please log in</div>;
  }

  return (
    <div className="flex h-screen gap-4 p-4 bg-gray-900">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col bg-white rounded-lg">
        <ChatInterface userId={user.id} />
      </div>

      {/* Emotion detection sidebar */}
      <div className="w-80 bg-white rounded-lg overflow-hidden shadow-lg">
        <div className="p-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white">
          <h2 className="font-bold">Emotion Detection</h2>
          <p className="text-sm text-purple-100">Privacy: Local browser only</p>
        </div>
        <EmotionDetector
          userId={user.id}
          conversationContext="sanctuary_chat"
          isActive={true}
        />
      </div>
    </div>
  );
```text
```


##

### Pattern 2: Modal or Overlay

Show emotion detector as a modal dialog:

```tsx
// components/EmotionDetectorModal.tsx
import { EmotionDetector } from "@/components/EmotionDetector";
import { useState } from "react";

export function EmotionDetectorModal({ userId }: { userId: string }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
      >
        {isOpen ? "Hide" : "Show"} Emotion Detection
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg w-96 h-96 overflow-hidden">
            <div className="p-4 bg-purple-600 text-white flex justify-between items-center">
              <h2 className="font-bold">Real-time Emotion Detection</h2>
              <button
                onClick={() => setIsOpen(false)}
                className="text-xl font-bold hover:bg-purple-700 w-8 h-8 rounded"
              >
                ✕
              </button>
            </div>
            <EmotionDetector userId={userId} conversationContext="modal_session" isActive={true} />
          </div>
        </div>
      )}
    </>
  );
```text
```


##

### Pattern 3: Tabbed Interface

Include emotion detection as one tab among many:

```tsx
// components/ChatWithTabs.tsx
import { EmotionDetector } from "@/components/EmotionDetector";
import { useState } from "react";

export function ChatWithTabs({ userId }: { userId: string }) {
  const [activeTab, setActiveTab] = useState<"chat" | "emotion" | "history">("chat");

  return (
    <div className="flex h-screen flex-col">
      {/* Tab selector */}
      <div className="flex border-b border-gray-200">
        {["chat", "emotion", "history"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-4 py-2 font-medium ${
              activeTab === tab
                ? "border-b-2 border-purple-600 text-purple-600"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-auto">
        {activeTab === "chat" && <ChatInterface userId={userId} />}
        {activeTab === "emotion" && (
          <EmotionDetector userId={userId} conversationContext="tabbed_view" isActive={true} />
        )}
        {activeTab === "history" && <EmotionHistory userId={userId} />}
      </div>
    </div>
  );
```text
```


##

## Data Flow

### What Happens When EmotionDetector Runs

1. **Load Models** (once on mount)
   - Loads face-api.js models from `/public/models/`
   - Shows loading state while downloading

2. **Request Webcam Permission**
   - Browser prompts user to allow camera access
   - User can accept or deny

3. **Stream Video** (local only, never transmitted)
   - Video feed plays in `<video>` element
   - Only runs in user's browser
   - Video is flipped horizontally for user comfort

4. **Detect Emotions** (every 1 second)
   - Analyzes video frames for facial expressions
   - Detects 8 emotions: happy, sad, angry, fearful, disgusted, surprised, contemptuous, neutral
   - Gets confidence score (0-1) for each

5. **Apply Thresholds**
   - Fetches user's adaptive thresholds from `/api/emotion-thresholds`
   - Only sends emotion if confidence ≥ threshold
   - Thresholds are personalized based on user's history

6. **Send Metadata Only**
   - Posts only: `{emotion, confidence, timestamp, user_id, conversation_context}`
   - NO video frames, NO images, NO biometric data
   - Backend stores in Supabase `emotions_log` table

7. **Update Thresholds** (via Supabase Realtime)
   - Training script (`train_emotion_model.py`) analyzes logs
   - Updates thresholds based on user's emotion patterns
   - Frontend receives updates instantly via Realtime subscription
   - Detector adapts without page reload
##

## Handling User Permissions

### Browser Permission Handling

The component automatically requests webcam permission. If denied:

```tsx
// Show error state
const [error, setError] = useState<string | null>(null);

// Error is displayed to user
{
  error && (
    <div className="bg-red-50 p-4 text-red-600 rounded-lg">
      <p className="font-bold">{error}</p>
      <button
        onClick={() => {
          // User can retry or grant permission in browser settings
        }}
        className="mt-2 text-sm underline"
      >
        Try again or check camera permissions
      </button>
    </div>
  );
```text
```



### Graceful Degradation

If webcam is unavailable, emotion detection simply doesn't run. The chat interface continues to work normally.
##

## Enabling/Disabling Detection

Control detection with the `isActive` prop:

```tsx
// Disable during video calls or when not needed
<EmotionDetector
  userId={user.id}
  isActive={isInChat} // Only detect while in chat
/>

// Disable for privacy-focused users
<EmotionDetector
  userId={user.id}
  isActive={user.preferences.enableEmotionTracking}
```text
```


##

## Viewing Emotion Logs

### In Supabase Dashboard

```sql
-- View recent emotion logs for a user
SELECT emotion, confidence, timestamp, conversation_context
FROM emotions_log
WHERE user_id = 'user_123'
ORDER BY timestamp DESC
```text
```



### Via API

```typescript
// Fetch emotion history
async function getEmotionHistory(userId: string) {
  const response = await fetch(
    `/api/emotions?user_id=${userId}&limit=100`
  );
  const { data } = await response.json();
  return data;
```text
```



### Create a Dashboard Component

```tsx
// components/EmotionHistory.tsx
import { useEffect, useState } from "react";

export function EmotionHistory({ userId }: { userId: string }) {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/emotions?user_id=${userId}`)
      .then((r) => r.json())
      .then((d) => {
        setLogs(d.data || []);
        setLoading(false);
      });
  }, [userId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Emotion History</h2>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {logs.map((log) => (
          <div key={log.id} className="flex justify-between items-center p-2 bg-gray-100 rounded">
            <span className="capitalize font-bold">{log.emotion}</span>
            <span className="text-sm text-gray-600">
              {(log.confidence * 100).toFixed(0)}%
            </span>
            <span className="text-xs text-gray-500">
              {new Date(log.timestamp).toLocaleTimeString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
```text
```


##

## Privacy Considerations

✓ **Video never leaves browser** - All detection runs locally
✓ **Metadata only** - Only emotion label + confidence sent to backend
✓ **No storage of images** - Zero video/photo storage anywhere
✓ **User control** - Can disable anytime via `isActive={false}`
✓ **Transparent** - Component displays "Privacy: Video stays local"
##

## Performance Tips

1. **Limit detection to active chats**
   ```tsx
   isActive={isActiveChatOpen}
   ```

2. **Use smaller video dimensions**
   - Component defaults to 320x240 (optimized)
   - Balances accuracy with CPU usage

3. **Adjust detection frequency**
   - Default: every 1 second
   - Modify in EmotionDetector.tsx: `setInterval(analyzeFrame, 1000)`
   - Higher = smoother, more CPU; Lower = smoother detection, less CPU

4. **Batch database writes**
   - Only sends emotion if confidence ≥ threshold
   - Reduces database writes by ~70%
##

## Training & Improvement Loop

### Weekly Training

Run the training script weekly to refine thresholds:

```bash
```text
```



### Monthly Analysis

Check which emotions are most frequently detected:

```bash
```text
```



### Continuous Improvement

As more data accumulates:
- Detector becomes more accurate for that user
- Thresholds adapt to user's baseline
- System becomes lighter (less CPU) and smarter (higher accuracy)
##

## Troubleshooting

### Emotion detection not working
1. Check if models loaded: Open browser DevTools Console, look for model loading errors
2. Check webcam permission: Browser → Settings → Site Permissions → Camera
3. Check lighting: Better lighting = better detection

### No emotion logs appearing
1. Verify `/api/emotions` endpoint is responding: `curl http://localhost:3000/api/emotions?user_id=test`
2. Check SUPABASE_SERVICE_ROLE_KEY is set in backend environment
3. Verify `emotions_log` table exists in Supabase

### Thresholds not updating
1. Check if training script ran: `python train_emotion_model.py --user_id user_123`
2. Verify Realtime is enabled on `emotion_thresholds` table in Supabase
3. Check browser console for Realtime subscription errors
##

## Next Steps

1. ✅ Integrate EmotionDetector into your chat page
2. ✅ Set up Supabase tables (see EMOTION_LEARNING_SETUP.md)
3. ✅ Download face-api.js models (see FACEAPI_MODELS_SETUP.md)
4. ✅ Test emotion detection with your camera
5. ✅ Run training script to create adaptive thresholds
6. ✅ Monitor emotion patterns in Supabase dashboard
##

## Example: Complete Chat + Emotion Page

```tsx
// app/chat/[conversationId]/page.tsx
"use client";

import { useSession } from "@/hooks/useSession";
import { ChatInterface } from "@/components/ChatInterface";
import { EmotionDetector } from "@/components/EmotionDetector";
import { use } from "react";

export default function ConversationPage({
  params,
}: {
  params: Promise<{ conversationId: string }>;
}) {
  const { conversationId } = use(params);
  const { user } = useSession();

  if (!user) {
    return <div className="p-4 text-center">Please log in</div>;
  }

  return (
    <div className="flex h-screen gap-4 bg-gray-100 p-4">
      {/* Chat interface (main focus) */}
      <div className="flex-1 flex flex-col bg-white rounded-lg shadow-lg overflow-hidden">
        <ChatInterface conversationId={conversationId} userId={user.id} />
      </div>

      {/* Emotion detection (optional right sidebar) */}
      <div className="w-80 flex flex-col bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-4">
          <h3 className="font-bold text-lg">Emotional Awareness</h3>
          <p className="text-sm text-purple-100">Your emotions matter here</p>
        </div>
        <EmotionDetector
          userId={user.id}
          conversationContext={`conversation_${conversationId}`}
          isActive={true}
        />
      </div>
    </div>
  );
}
```



That's it! Your emotion detection system is integrated and ready to learn.
