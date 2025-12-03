# firstperson (Expo), minimal scaffold

This folder contains a minimal Expo React Native app used to test the `firstperson` mobile client against the Python FastAPI backend in this repo.

Quick start (development):

1. Install deps

```bash
cd firstperson
npm install
```

2. Start the Expo dev server

```bash
npx expo start
```

3. Open on device or emulator

- Scan the QR code with the Expo Go app (Android/iOS) or run on simulators from the Expo devtools.

Backend configuration

- By default the app points at `http://localhost:8000`. To change this, set the environment variable `REACT_APP_SAOYNX_API_URL` before starting the app. Example:

```bash
REACT_APP_SAOYNX_API_URL="http://192.168.1.100:8000" npx expo start
```

EAS (optional)

- If you plan to use EAS Build / Submit, run:

```bash
cd firstperson
eas build:configure
```

This project includes a minimal `eas.json` so the command will not fail. Note that EAS requires an Expo account and `eas-cli` to be installed and logged in.

Files of interest

- `src/config.js`, controls the backend URL and provides `postMessage` used by the UI.
- `App.js`, app entry.

If you want, I can run a quick smoke test (POST a message to the FastAPI `/api/chat`) from a tiny node script here to verify connectivity to your running backend.
