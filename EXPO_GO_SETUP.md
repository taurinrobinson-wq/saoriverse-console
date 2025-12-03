# FirstPerson Expo Go Setup Guide

## Quick Start - Run in Expo Go

### Option 1: Using Tunnel Mode (Recommended - Works Remotely)

```bash
cd /workspaces/saoriverse-console/firstperson
npm install
npx expo start --tunnel
```

This will output a QR code in your terminal. Scan it with:

- **iPhone**: Open Camera app, point at QR code, tap notification
- **Android**: Open Expo Go app, tap "Scan QR Code"

### Option 2: Using LAN Mode (Local Network)

```bash
cd /workspaces/saoriverse-console/firstperson
npm install
npx expo start --lan
```

Then scan the QR code with Expo Go on your device.

### Option 3: Using Local Mode (Same Machine)

```bash
cd /workspaces/saoriverse-console/firstperson
npm install
npx expo start
```

Then press:

- `i` to open iOS Simulator
- `a` to open Android Emulator
- `w` to open web browser

## What You'll See in the App

The FirstPerson app includes:

### 1. **Chat Screen** 📱

- Send messages to the emotional AI
- See responses with glyph symbols (◆)
- View prosody metadata (emotion, tone, glyphs)

### 2. **Multimodal Affect Display** 🎯

- **Voice Analysis**: emotion, arousal, valence
- **Facial Analysis**: expression, intensity
- **Text Analysis**: sentiment, emotion
- **Fusion**: combined multimodal emotion
- Expandable view with confidence bars

### 3. **Multimodal Input** (When backend ready)

- Voice input capture
- Facial expression detection
- Text-based emotions

### 4. **Settings Screen** ⚙️

- Configure API endpoint
- Choose processing mode (local/remote)
- Manage preferences

## App Architecture

```
FirstPerson (React Native + Expo)
├── src/screens/
│   ├── ChatScreen.js          ← Main chat UI
│   ├── SettingsScreen.js
│   └── OnboardingScreen.js
├── src/components/
│   ├── MessageBubble.js          ← Renders messages + prosody
│   ├── MultimodalAffectDisplay.js  ← Shows voice/facial/text affect
│   ├── MultimodalInput.js           ← Captures multimodal input
│   └── ChatInput.js
├── src/services/
│   ├── ApiService.js               ← Backend communication
│   ├── StorageService.js           ← Local data storage
│   └── SyncService.js              ← Offline sync
└── App.js                          ← Root component
```

## Backend Integration

The app connects to the FastAPI server at:

- **Default**: `http://localhost:3000/api/chat`
- **Change in**: Settings Screen → API Configuration

### Required Backend Response Format

```json
{
  "success": true,
  "reply": "Your response text",
  "glyph": {
    "name": "Grounded",
    "symbol": "◆",
    "confidence": 0.85
  },
  "affect": {
    "voice": {
      "emotion": "calm",
      "arousal": 0.3,
      "valence": 0.7,
      "confidence": 0.8
    },
    "facial": {
      "emotion": "neutral",
      "intensity": 0.5,
      "confidence": 0.6
    },
    "text": {
      "emotion": "positive",
      "sentiment": 0.7,
      "confidence": 0.75
    },
    "fusion": {
      "primary_emotion": "calm",
      "confidence": 0.82
    }
  },
  "processing_time": 0.234
}
```

## Testing the Multimodal UI

1. Start the app in Expo Go
2. Send a message
3. Wait for response
4. If backend returns affect data, you'll see: **"🎯 Show Affect Analysis"**
5. Tap to expand and see voice/facial/text affect breakdown

## Troubleshooting

### QR Code Not Displaying

```bash
npx expo start --tunnel --clear
```

### Metro Bundler Hangs

```bash
npx expo start --tunnel --reset-cache
```

### Connection Issues

Check that your device is on same network (LAN mode) or has internet (tunnel mode).

### Backend Not Responding

1. Verify API endpoint in Settings
2. Check backend is running: `python -m uvicorn emotional_os.deploy.fastapi_app:app --reload`
3. Test endpoint: `curl http://localhost:3000/api/chat`

## Development Tips

### Hot Reload

- Save any `.js` file to see changes instantly
- The app will refresh automatically

### Debug Messages

Enable debug logs in Settings → Debug Mode

### View Console

Press `j` in terminal while app is running to open debugger

### Stop Server

Press `Ctrl+C` in terminal

## Files to Customize

- **`App.js`**: Root app navigation
- **`src/screens/ChatScreen.js`**: Main UI layout
- **`src/components/MessageBubble.js`**: Message rendering
- **`src/services/ApiService.js`**: Backend API calls
- **`firstperson/package.json`**: Dependencies

## Next Steps

1. ✅ Install dependencies: `npm install`
2. ✅ Start Expo: `npx expo start --tunnel`
3. 📱 Scan QR code with Expo Go
4. 💬 Send a message
5. 🎯 See multimodal affect display (when backend ready)

Happy testing! 🚀
