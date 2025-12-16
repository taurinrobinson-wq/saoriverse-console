# face-api.js Models Setup

## Overview
The `EmotionDetector.tsx` component requires pre-trained models from `face-api.js` library. These models must be downloaded and placed in your Next.js `public/models` directory.

## Step 1: Download Models

The face-api.js library uses models from the `face-api.js` repository. You have two options:

### Option A: Download via NPM (Recommended)

First, install face-api.js:

```bash
cd firstperson-web
npm install face-api.js
```



Then copy models from node_modules:

```bash

# Windows PowerShell
Copy-Item node_modules/face-api.js/dist/models -Destination public/models -Recurse -Force

# macOS/Linux
cp -r node_modules/face-api.js/dist/models public/models
```



### Option B: Manual Download

1. Clone or download the face-api.js repository:
   - GitHub: https://github.com/vladmandic/face-api

2. Navigate to `dist/models` folder

3. Copy all model files to `firstperson-web/public/models/`

## Step 2: Verify Models are in Place

Your `public/models` directory should contain these files:

```
public/models/
├── tiny_face_detector_model-weights_manifest.json
├── tiny_face_detector_model-weights_shard_1
├── tiny_face_detector_model.json
├── face_expression_model-weights_manifest.json
├── face_expression_model-weights_shard_1
├── face_expression_model.json
├── (additional model files as needed)
```



### Check via file system:

```bash

# Windows PowerShell
Get-ChildItem -Path "firstperson-web/public/models" -File

# macOS/Linux
ls -la firstperson-web/public/models/
```



You should see at least:
- `tiny_face_detector_model.*` (3 files)
- `face_expression_model.*` (3 files)

## Step 3: Update Next.js Configuration (if needed)

Ensure Next.js serves the models directory correctly:

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  staticFileGlobs: ['public/**/*'],
  // your other config here
};

module.exports = nextConfig;
```



Usually this is already configured by default in Next.js 13+.

## Step 4: Test Models Load Correctly

Add a simple test in your app to verify models load:

```typescript
// pages/api/test-models.ts
import * as faceapi from "face-api.js";

export default async function handler(req: any, res: any) {
  try {
    await faceapi.nets.tinyFaceDetector.loadFromUri("/models");
    await faceapi.nets.faceExpressionNet.loadFromUri("/models");

    res.status(200).json({
      success: true,
      message: "Models loaded successfully"
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
```



Then test:

```bash
curl http://localhost:3000/api/test-models
```



Expected response:

```json
{
  "success": true,
  "message": "Models loaded successfully"
}
```



## Step 5: Optimize Model Loading (Optional)

For faster page loads, you can load models asynchronously:

```typescript
// lib/faceapi-loader.ts
import * as faceapi from "face-api.js";

let modelsLoaded = false;

export async function loadFaceApiModels() {
  if (modelsLoaded) return;

  try {
    const modelsPath = "/models";
    await Promise.all([
      faceapi.nets.tinyFaceDetector.loadFromUri(modelsPath),
      faceapi.nets.faceExpressionNet.loadFromUri(modelsPath),
    ]);
    modelsLoaded = true;
    console.log("✓ Face-API models loaded successfully");
  } catch (error) {
    console.error("✗ Failed to load Face-API models:", error);
    throw error;
  }
}

export function areModelsLoaded() {
  return modelsLoaded;
}
```



## Troubleshooting

### Problem: "Failed to load face detection models"
**Solutions:**
1. Verify files exist in `public/models/` directory
2. Check browser console for 404 errors (path might be wrong)
3. Ensure models are in the correct location (case-sensitive on Linux/Mac)
4. Try clearing browser cache and rebuilding Next.js

### Problem: CORS errors when loading models
**Solution:** The models should be served from the same domain (already configured in `public/`). If you get CORS errors, check:
1. Models are in `public/models/` (not elsewhere)
2. Next.js development server is running
3. You're accessing via `http://localhost:3000` (not `127.0.0.1`)

### Problem: Models load but detection doesn't work
**Solutions:**
1. Check browser console for errors in face detection
2. Verify video element has a valid stream (check browser permissions)
3. Ensure video dimensions are >= 100x100 pixels
4. Test with better lighting conditions

### Problem: High memory usage or slow detection
**Solutions:**
1. Use `TinyFaceDetector` (already done in EmotionDetector.tsx) — it's optimized for mobile
2. Reduce detection frequency: change `setInterval(analyzeFrame, 1000)` to 2000 or higher
3. Reduce video dimensions: set `{ video: { width: 320, height: 240 } }`
4. Enable hardware acceleration in browser settings

## Model Details

### TinyFaceDetector
- **Size:** ~500 KB
- **Inference time:** ~20-50ms per frame (CPU)
- **Accuracy:** Good for real-time detection
- **License:** MIT

### FaceExpressionNet
- **Size:** ~250 KB
- **Detects:** happy, sad, angry, fearful, disgusted, surprised, neutral
- **Confidence:** 0-1 per emotion
- **License:** MIT

## Download Sizes & Bandwidth

- **Total model files:** ~1.2 MB
- **First load:** ~5-10 seconds (includes download + parsing)
- **Subsequent loads:** Cached by browser (milliseconds)

**Tip:** Users only need to download models once. Use service workers for offline support:

```typescript
// In your service worker registration
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
    .then(reg => console.log('Service Worker registered'))
    .catch(err => console.log('SW registration failed'));
}
```



## Privacy Note

⚠️ **Important:** All models run locally in the browser. No facial data, emotions, or video frames are transmitted to any server. Only emotion metadata (`{emotion, confidence}`) is sent to your backend.
##

## Summary

1. ✅ Install face-api.js: `npm install face-api.js`
2. ✅ Copy models to `public/models/`
3. ✅ Verify files exist
4. ✅ Test loading via `/api/test-models`
5. ✅ Use EmotionDetector component in your pages

That's it! Your emotion detection system is ready.
