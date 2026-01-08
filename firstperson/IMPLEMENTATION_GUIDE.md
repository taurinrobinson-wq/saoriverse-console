# FirstPerson Mobile – React Native MVP Implementation Guide

## Project Overview

**FirstPerson Mobile** is a standalone React Native (Expo) application for iOS and Android that provides emotionally attuned AI companionship with **prosody awareness**, **local-first privacy**, and **offline-first sync**.

### Key Features (MVP)

✅ **Onboarding Ritual** - 3-step guided flow (Welcome → Mode Selection → Personalization)
✅ **Multi-Mode First Turn** - Ritual, Casual, or Reflective conversation starter
✅ **Prosody-Aware Responses** - Displays emotions, glyphs, confidence scores, tone
✅ **Memory Capsules** - Relational context snapshots saved every 5 messages
✅ **Local-First Storage** - All conversations stored privately on device via AsyncStorage
✅ **Offline-First Sync** - Messages queue when offline, auto-sync when online
✅ **Settings Dashboard** - Preferences, conversation management, privacy controls
✅ **Streamlined UI** - Bottom tab navigation (Chat, Settings) with minimal cognitive load

##

## Project Structure

```text
```


firstperson/
├── App.js                          # Main entry point with navigation setup
├── index.js                        # Expo app entry
├── app.json                        # Expo configuration
├── eas.json                        # EAS Build configuration
├── package.json                    # Dependencies (updated)
├── src/
│   ├── config.js                   # Backend API configuration (existing)
│   ├── screens/
│   │   ├── ChatScreen.js          # 🆕 Main chat interface
│   │   ├── OnboardingScreen.js    # 🆕 Onboarding flow
│   │   ├── SettingsScreen.js      # 🆕 Settings & preferences
│   │   └── MessageOverlay.js      # 📦 Legacy (archived)
│   ├── components/
│   │   ├── MessageBubble.js       # 🆕 Message display with prosody
│   │   ├── ChatInput.js           # 🆕 Enhanced input component
│   │   └── ...
│   └── services/
│       ├── ApiService.js          # 🆕 Backend integration
│       ├── StorageService.js      # 🆕 Local persistence layer
│       └── SyncService.js         # 🆕 Offline-first sync
└── assets/                         # Icons, images, splash screens

```


##

## Core Components & Services

### 1. **Services Layer**

#### `StorageService.js`

Manages all local data using `@react-native-async-storage/async-storage`.

**Key Functions:**

- `addMessageToConversation(conversationId, message)` - Save chat messages
- `getConversation(conversationId)` - Retrieve full conversation history
- `getAllConversations()` - List all conversations with summaries
- `createMemoryCapsule(conversationId, capsuleData)` - Save relational context snapshots
- `getMemoryCapsules(conversationId)` - Retrieve stored memory capsules
- `setUserPreferences(preferences)` - Store user settings (theme, mode, etc)
- `queueMessageForSync(message)` - Queue messages for offline support
- `getSyncQueue()` / `clearSyncQueue()` - Manage sync queue
- `setOnboardingComplete(userId)` / `isOnboardingComplete()` - Track onboarding state

**Storage Keys:**
```text

```text
```


fp_conversations         # All conversations and messages
fp_memory_capsules      # Relational context snapshots
fp_user_prefs           # User preferences (theme, notifications, etc)
fp_sync_queue           # Messages queued during offline
fp_onboarding_complete  # Onboarding completion marker

```



##

#### `ApiService.js`

Handles all backend communication with prosody parsing and offline detection.

**Key Functions:**

- `sendMessage(text, options)` - Send message to `/api/chat`
  - Returns: `{ success, reply, prosody, processingTime, glyphs, offline? }`
  - Prosody includes: emotion, confidence, intensity, tone, glyphs array
  - Auto-queues for sync on network error

- `getConversationHistory(conversationId, options)` - Fetch server-side history
- `getGlyphs(options)` - Get available glyphs library
- `testConnectivity()` - Check backend health
- `parseProsodyMetadata(response)` - Extract emotion/glyph/tone metadata

**Prosody Structure:**

```javascript

{
  emotion: "melancholy",         // e.g., joy, sadness, anger, etc
  confidence: 0.87,              // 0.0 - 1.0
  intensity: "high",             // gentle, moderate, high
  tone: "reflective",            // tone of response
  glyphs: [
    { name: "Ember", score: 0.92, symbol: "🔥", description: "..." },
    { name: "Echo", score: 0.78, symbol: "📍", description: "..." }
  ]

```text
```text

```

##

#### `SyncService.js`

Implements offline-first sync with listener pattern for UI updates.

**Key Functions:**

- `performSync()` - Process sync queue, retry failed messages
  - Returns: `{ success, syncedCount, errors? }`
  - Notifies listeners of progress

- `getSyncStatus()` - Current sync state
- `onSyncStatusChange(callback)` - Subscribe to sync events
  - Fires: `{ syncing, syncedCount, errors?, queuedMessages }`

##

### 2. **Screen Components**

#### `ChatScreen.js`

Main chat interface with real-time message display and prosody rendering.

**Features:**

- Load conversation history from local storage on mount
- Display messages with `MessageBubble` component
- Render prosody metadata: emotion labels, glyph symbols, confidence %
- Create memory capsules every 5 messages
- Handle offline messages (queue for sync)
- Auto-scroll to latest message
- Show loading state during message processing

**Flow:**

1. User types message → ChatInput
2. Message saved to local storage immediately (optimistic)
3. Sent to backend API
4. Response displayed with prosody metadata
5. Memory capsule created (every 5 messages)
6. All persisted to AsyncStorage

##

#### `OnboardingScreen.js`

3-step guided first-use flow with mode selection and personalization.

**Steps:**

1. **Welcome** - App intro, privacy assurance
2. **First-Turn Mode Selection** - Ritual 🕯️ / Casual 💬 / Reflective 🧘
3. **Personalization** - Optional name entry, privacy confirmation

**Features:**

- Mode cards with icons and descriptions
- Smooth step transitions
- Skip option available
- Stores preferences to AsyncStorage
- Marks onboarding complete
- Navigates to main app on completion

##

#### `SettingsScreen.js`

User preferences, conversation management, and privacy controls.

**Sections:**

1. **Statistics** - Conversations, total messages, storage used
2. **Preferences** - Dark mode, notifications, analytics toggle
3. **Conversations** - List with export buttons (future feature)
4. **Privacy & Security** - Info card, links to policies
5. **About** - Version, backend info
6. **Danger Zone** - Clear all data (with confirmation)

##

### 3. **Component Components**

#### `MessageBubble.js`

Displays individual messages with optional prosody metadata.

**Props:**

```javascript


{
  message: {
    role: "user" | "assistant",
    text: string,
    prosody?: {...},              // Optional metadata
    timestamp?: ISO string,
  },
  theme: "light" | "dark"

```text
```


**Rendering:**

- User messages: right-aligned, green background
- Assistant messages: left-aligned, gray background
- Prosody metadata: emotion emoji + confidence, glyph symbols, tone
- Timestamp in subtle text below message

##

#### `ChatInput.js`

Enhanced message input with multi-line support and sending state.

**Features:**

- Multi-line text input (max 2000 chars)
- Send button with loading indicator
- Disabled state management
- Auto-focus optimizations
- Accessibility support

##

## Data Flow Architecture

### Message Send Flow

```
User Input
    ↓
ChatInput Component (onSend)
    ↓
ChatScreen.handleSendMessage()
    ↓
├─ Store user message locally (optimistic UI)
├─ Call ApiService.sendMessage()
│   ├─ Send to /api/chat
│   ├─ Parse prosody metadata
│   └─ On error: Queue for offline sync
├─ Display assistant response with prosody
├─ Store assistant message locally
```text

```text
```


### Offline Sync Flow

```

Network Offline
    ↓
ApiService detects network error
    ↓
Message queued via StorageService.queueMessageForSync()
    ↓
UI shows: "📡 Message queued. Will send when connected."
    ↓
App detects connection restored
    ↓
SyncService.performSync() triggered
    ↓
├─ Fetch sync queue from storage
├─ Retry each queued message
├─ Save successful responses to conversation
└─ Clear sync queue
    ↓

```text

```

##

## Installation & Setup

### Prerequisites

```bash


# Install Node.js 18+
node --version

# Install Expo CLI
npm install -g expo-cli

# Install EAS CLI (for building)

```text
```text

```

### Quick Start

```bash


cd /workspaces/saoriverse-console/firstperson

# Install dependencies
npm install

# Start Expo dev server
npm start

# Scan QR code with Expo Go app (iOS/Android)

# Or launch emulator:

# - Android: npm run android

# - iOS: npm run ios

# Test on device:

# - Physical device: Expo Go app → Scan QR

```text
```


### Environment Setup

```bash

# Configure backend URL (in src/config.js):
REACT_APP_SAOYNX_API_URL=http://192.168.1.100:8000  # Replace with your IP

# Or in environment:
export REACT_APP_SAOYNX_API_URL="http://192.168.1.100:8000"
```text

```text
```


##

## Dependencies

**Added for this MVP:**

```json

{
  "@react-native-async-storage/async-storage": "^1.21.0",    // Local storage
  "@react-native-community/netinfo": "^11.0.2",              // Network detection
  "expo-constants": "~15.4.5",                                // Debugger host detection
  "react-native-gesture-handler": "^2.14.1",                 // Navigation
  "react-native-reanimated": "^3.6.0",                        // Animations
  "react-native-safe-area-context": "^4.7.2",               // Safe area
  "react-native-screens": "^3.27.0",                         // Screen handling
  "react-navigation": "^4.4.4",                              // Navigation framework
  "react-navigation-bottom-tabs": "^6.4.0",                  // Bottom tab nav
  "react-navigation-native": "^6.1.9",                       // Navigation native
  "react-navigation-stack": "^6.3.20"                        // Stack navigation

```text

```

##

## Next Steps (Future Enhancements)

### Phase 2 - Smart Features

- [ ] **Clarification Prompts** - Modal UI for ambiguous input detection
- [ ] **Conversation Pinning** - Mark important conversations
- [ ] **Export Conversations** - JSON/PDF export feature
- [ ] **Dark Mode** - Full theme support with user preference

### Phase 3 - Advanced Sync

- [ ] **NetInfo Integration** - Auto-detect network changes
- [ ] **Conflict Resolution** - Handle sync conflicts gracefully
- [ ] **Server Sync** - Sync conversations to cloud (optional)

### Phase 4 - Deployment

- [ ] **EAS Build** - Generate iOS/Android binaries
- [ ] **TestFlight** - iOS beta testing
- [ ] **Google Play Beta** - Android beta testing
- [ ] **App Store** - Production releases

### Phase 5 - Polish

- [ ] **Notification Center** - Local push notifications
- [ ] **Share Feature** - Share conversations securely
- [ ] **Accessibility** - Full VoiceOver/TalkBack support
- [ ] **Performance** - Optimize list rendering, reduce bundle size

##

## Testing Checklist

### Functional Testing

- [ ] Onboarding flow completes without errors
- [ ] Messages send and display correctly
- [ ] Prosody metadata renders accurately
- [ ] Memory capsules created at right intervals
- [ ] Local storage persists across app restarts
- [ ] Settings save and apply correctly
- [ ] Offline queue triggers on network error
- [ ] Sync completes successfully when online

### Integration Testing

- [ ] Backend API responds correctly
- [ ] Emotion/glyph metadata parsed properly
- [ ] Error messages display user-friendly text
- [ ] Network reconnection triggers auto-sync

### Edge Cases

- [ ] Very long messages (2000+ chars)
- [ ] Rapid message sending
- [ ] App backgrounded during sync
- [ ] Device offline for extended period
- [ ] Low storage conditions

##

## Troubleshooting

### Common Issues

**"Cannot connect to backend"**

```bash


# Check backend is running
curl http://localhost:8000/health

# Check IP address is correct in config.js

# For device on same WiFi: use computer's LAN IP, not localhost
ipconfig getifaddr en0  # macOS

```text
```text

```

**"AsyncStorage not working"**

```bash



# Ensure package is installed
npm list @react-native-async-storage/async-storage

# Clear cache and reinstall
rm -rf node_modules

```text
```


**"Navigation not working"**

```bash

# Ensure all navigation dependencies installed
npm install @react-navigation/native @react-navigation/bottom-tabs

# Clear Expo cache
expo start -c
```


##

## Developer Notes

- **State Management**: Using Context API for simplicity (suitable for MVP)
- **Backend Integration**: Expects `/api/chat` endpoint returning `{ success, reply, prosody, glyphs }`
- **Error Handling**: Graceful degradation with local-only fallback
- **Accessibility**: Components designed with VoiceOver compatibility
- **Performance**: Message list virtualization ready (FlatList)
- **Privacy**: No analytics by default; all data local unless explicitly shared

##

## Files Modified/Created This Session

**New Files (11):**

1. ✅ `App.js` - Main app with navigation
2. ✅ `src/screens/ChatScreen.js` - Chat interface
3. ✅ `src/screens/OnboardingScreen.js` - Onboarding flow
4. ✅ `src/screens/SettingsScreen.js` - Settings interface
5. ✅ `src/components/MessageBubble.js` - Message display
6. ✅ `src/components/ChatInput.js` - Input component
7. ✅ `src/services/ApiService.js` - Backend integration
8. ✅ `src/services/StorageService.js` - Local storage
9. ✅ `src/services/SyncService.js` - Offline sync
10. ✅ `package.json` - Updated dependencies
11. ✅ This guide document

**Existing Files Updated:**

- None breaking; legacy `MessageOverlay.js` preserved

##

## Deployment Guide (Coming Next Phase)

See `Offshoots/FirstPerson-Mobile/FirstPerson-Mobile.md` for MVP spec.

**Quick Deploy Checklist:**

1. Configure EAS Build: `eas build:configure`
2. Build for iOS: `eas build --platform ios --distribution testflight`
3. Build for Android: `eas build --platform android --distribution play`
4. Submit to TestFlight / Play Store
5. Monitor for crash reports
6. Iterate on user feedback

##

**Status**: ✅ MVP Core Complete - Ready for Alpha Testing
**Last Updated**: December 3, 2025
**Maintainer**: FirstPerson Team
