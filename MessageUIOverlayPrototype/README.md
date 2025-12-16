# MessageUI Overlay Prototype

A React Native / Expo prototype demonstrating the core UI components for the Message UI Overlay feature - a manipulation and gaslighting detection system for messaging apps.

## 📱 Features

- **Text Input**: Enter or paste sample iMessage text for analysis
- **Heatmap Overlay**: Visual highlighting of detected manipulation patterns with severity levels (high, medium, low)
- **Reframe Button**: Inline suggestions for healthier communication alternatives
- **Sample Messages**: Pre-loaded examples demonstrating various manipulation patterns

## 🚀 Getting Started

### Prerequisites

1. **Node.js** (v18 or later recommended)
2. **Expo Go app** installed on your mobile device:
   - [iOS App Store](https://apps.apple.com/app/expo-go/id982107779)
   - [Android Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)

### Installation

1. Navigate to the prototype directory:

   ```bash
   cd MessageUIOverlayPrototype
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

### Running the Prototype

1. Start the Expo development server:

   ```bash
   npx expo start
   ```

2. A QR code will appear in your terminal.

3. **On iOS**: Open the Camera app and scan the QR code. It will prompt you to open in Expo Go.

4. **On Android**: Open the Expo Go app and scan the QR code using the built-in scanner.

5. The app will load on your device!

### Alternative: Run in Web Browser

You can also run the prototype in a web browser:

```bash
```text

```text
```


## 📁 Project Structure

```

MessageUIOverlayPrototype/
├── App.js              # Main entry point with text input and overlay showcase
├── HeatmapOverlay.js   # Component for displaying text with heatmap highlights
├── ReframeButton.js    # Component for inline reframe suggestions
├── app.json            # Expo configuration
├── package.json        # Dependencies and scripts
├── babel.config.js     # Babel configuration for Expo
├── assets/             # Icon and splash screen assets
└── README.md           # This file

```


## 🧩 Components

### HeatmapOverlay

Displays text with color-coded highlights indicating manipulation severity:

- 🔴 **High severity**: Red highlighting (e.g., gaslighting, denial)
- 🟠 **Medium severity**: Orange highlighting (e.g., guilt-tripping)
- 🟡 **Low severity**: Yellow highlighting (e.g., minor manipulation)

### ReframeButton

An inline button component that appears when highlighted text is tapped:

- Shows a suggested healthier alternative phrase
- "Apply Reframe" replaces the manipulative text with the suggestion
- "Dismiss" hides the suggestion

## 🔮 Mock Data

This prototype uses mock data for demonstration purposes. The following manipulation patterns are recognized:

1. "You're being too sensitive about this."
2. "I never said that, you're imagining things."
3. "Everyone agrees with me, you're the only one who doesn't see it."
4. "After everything I've done for you, this is how you treat me?"
5. "If you really loved me, you wouldn't question my decisions."

In the full implementation, an ML classifier would analyze messages in real-time.

## 🛠 Tech Stack

- **React Native** - Cross-platform mobile framework
- **Expo** - Development platform for React Native
- **Expo Go** - Client app for testing on physical devices

## 📋 Next Steps (Future Development)

Based on the [MessageUI_Overlay MVP Spec](../Offshoots/MessageUI_Overlay/MessageUI_Overlay.md):

- [ ] Integrate ML classifier for real manipulation detection
- [ ] Add salience explainability for detection reasoning
- [ ] Implement local-first processing for privacy
- [ ] Add keyboard extension integration
- [ ] Conduct adversarial testing
- [ ] Prepare for closed beta testing

## 📄 License

Part of the Saoriverse Console project.
