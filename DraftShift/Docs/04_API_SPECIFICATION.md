# DraftShift API Specification: FastAPI Contract

## 📡 API Overview

The FastAPI backend exposes DraftShift's full civility analysis and transformation pipeline. This specification defines the exact request/response contract for the frontend and any third-party integrations.

**Base URL**: `http://localhost:8000` (development) or `https://your-domain.com` (production)

---

## 🔌 Endpoints

### 1. POST `/analyze`

**Purpose**: Analyze correspondence for civility compliance and provide transformation suggestions.

**Request Body**
```json
{
  "text": "We strongly object to your position and demand immediate compliance.",
  "mode": "civility",
  "include_rewrite": true
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `text` | string | ✅ Yes | Raw correspondence to analyze (max 5000 chars). |
| `mode` | string | ❌ No | One of: `civility` (default), `litigation`, `client-friendly`, `neutral-negotiation`. |
| `include_rewrite` | boolean | ❌ No | If `true`, generates a suggested rewrite (slower). Default: `true`. |

**Response (200 OK)**
```json
{
  "disclaimer": "DraftShift does not replace the role of an attorney...",
  "civility_score": 42,
  "civility_status": "red",
  "analysis": {
    "sentiment_polarity": -0.45,
    "sentiment_subjectivity": 0.72,
    "primary_emotion": "anger",
    "emotion_scores": {
      "anger": 0.68,
      "fear": 0.12,
      "joy": 0.02,
      "sadness": 0.15,
      "trust": 0.08
    },
    "valence": -0.35,
    "arousal": 0.82,
    "dominance": 0.55
  },
  "signals": {
    "primary_signal": "β",
    "primary_signal_name": "Boundary/Protective",
    "all_signals": ["β", "λ", "ε"],
    "signal_scores": {
      "α": 0.15,
      "β": 0.82,
      "γ": 0.08,
      "θ": 0.35,
      "λ": 0.65,
      "ε": 0.42,
      "Ω": 0.12
    }
  },
  "glyphs": [
    {
      "glyph": "⚖️",
      "name": "Boundary",
      "confidence": 0.82,
      "explanation": "Strong protective/boundary language detected."
    },
    {
      "glyph": "⚠️",
      "name": "Aggression",
      "confidence": 0.68,
      "explanation": "Negative sentiment and anger emotion detected."
    }
  ],
  "risk_alerts": [
    {
      "severity": "high",
      "message": "Tone may be perceived as dismissive or aggressive.",
      "trigger": "Phrase: 'We strongly object'",
      "suggestion": "Consider: 'We respectfully disagree with your position'"
    },
    {
      "severity": "medium",
      "message": "Demand language may escalate tension.",
      "trigger": "Phrase: 'demand immediate compliance'",
      "suggestion": "Consider: 'request your prompt response' or 'kindly respond by [date]'"
    }
  ],
  "suggested_rewrite": "We respectfully disagree with your position and request your prompt response to our concerns.",
  "rewrite_civility_score": 78,
  "rewrite_status": "yellow",
  "tools_active": {
    "nrc_lexicon": true,
    "spacy": true,
    "textblob": true,
    "affect_parser": true,
    "tone_composer": true,
    "local_llm": true
  }
}
```

**Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `disclaimer` | string | Legal disclaimer about attorney responsibility. |
| `civility_score` | integer (0-100) | Overall civility compliance score. |
| `civility_status` | string | `green` (80-100), `yellow` (60-79), `red` (0-59). |
| `analysis` | object | Detailed emotion, valence, arousal, dominance metrics. |
| `signals` | object | 7-signal tone analysis (α-Ω) with confidence scores. |
| `glyphs` | array | Symbolic overlays for dashboard visualization. |
| `risk_alerts` | array | Specific flagged issues with severity and suggestions. |
| `suggested_rewrite` | string | LLM-generated civility-compliant version (if requested). |
| `rewrite_civility_score` | integer | Civility score of suggested rewrite. |
| `rewrite_status` | string | Status of rewrite (`green`, `yellow`, `red`). |
| `tools_active` | object | Flags indicating which analysis tools are operational. |

**Error Response (400 Bad Request)**
```json
{
  "error": "Text exceeds maximum length of 5000 characters.",
  "status_code": 400
}
```

**Error Response (503 Service Unavailable)**
```json
{
  "error": "Local LLM backend unavailable. Analysis available without transformations.",
  "status_code": 503,
  "fallback_response": { ...analysis without rewrite... }
}
```

---

### 2. POST `/batch-analyze`

**Purpose**: Analyze multiple correspondence items in one request (for archives, bulk assessment).

**Request Body**
```json
{
  "documents": [
    { "id": "doc-001", "text": "Dear opposing counsel...", "mode": "civility" },
    { "id": "doc-002", "text": "Your honor, I object...", "mode": "litigation" }
  ],
  "include_rewrites": false
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `documents` | array | ✅ Yes | Array of `{id, text, mode}` objects. Max 50 documents per request. |
| `include_rewrites` | boolean | ❌ No | If `true`, generates rewrites for all (slower). Default: `false`. |

**Response (200 OK)**
```json
{
  "batch_id": "batch-20250619-abc123",
  "total_documents": 2,
  "results": [
    {
      "id": "doc-001",
      "civility_score": 85,
      "civility_status": "green",
      "analysis": { ...same as /analyze... }
    },
    {
      "id": "doc-002",
      "civility_score": 72,
      "civility_status": "yellow",
      "analysis": { ...same as /analyze... }
    }
  ],
  "summary": {
    "average_civility": 78.5,
    "distribution": {
      "green": 1,
      "yellow": 1,
      "red": 0
    }
  }
}
```

---

### 3. GET `/health`

**Purpose**: Check service status and available tools.

**Response (200 OK)**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-06-19T14:32:15Z",
  "components": {
    "nrc_lexicon": { "status": "ready", "loaded": true },
    "spacy_model": { "status": "ready", "model": "en_core_web_sm" },
    "textblob": { "status": "ready" },
    "signal_parser": { "status": "ready" },
    "llm_backend": { "status": "ready", "model": "mistral-7b-instruct", "backend": "gpt4all" }
  },
  "uptime_seconds": 3600
}
```

---

### 4. POST `/settings`

**Purpose**: Configure analysis parameters (model selection, sensitivity thresholds).

**Request Body**
```json
{
  "civility_threshold_alert": 70,
  "include_nrc_emotions": true,
  "include_signal_analysis": true,
  "llm_temperature": 0.7,
  "llm_max_tokens": 500,
  "language": "en-US"
}
```

**Response (200 OK)**
```json
{
  "settings": { ...updated settings... },
  "message": "Settings updated successfully."
}
```

---

### 5. GET `/models`

**Purpose**: List available local LLM models and their status.

**Response (200 OK)**
```json
{
  "available_models": [
    {
      "id": "mistral-7b-instruct-v0.1.Q4_0",
      "name": "Mistral 7B Instruct (Quantized)",
      "size_gb": 3.8,
      "quantization": "Q4_0",
      "loaded": true,
      "response_time_ms": 250
    },
    {
      "id": "llama3-8b.Q5_K_M",
      "name": "Llama 3 8B (Medium Quantization)",
      "size_gb": 5.2,
      "quantization": "Q5_K_M",
      "loaded": false,
      "response_time_ms": null
    }
  ],
  "current_model": "mistral-7b-instruct-v0.1.Q4_0"
}
```

---

### 6. POST `/export-report`

**Purpose**: Generate a compliance report (for California Rule 9.7 annual declaration).

**Request Body**
```json
{
  "document_ids": ["doc-001", "doc-002", "doc-003"],
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-06-30"
  },
  "format": "pdf"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `document_ids` | array | ✅ Yes | IDs of documents to include in report. |
| `date_range` | object | ✅ Yes | Start and end dates for report period. |
| `format` | string | ❌ No | `pdf` (default), `markdown`, `csv`. |

**Response (200 OK)**
```json
{
  "report_id": "report-20250619-xyz789",
  "format": "pdf",
  "url": "/downloads/report-20250619-xyz789.pdf",
  "summary": {
    "total_documents": 3,
    "average_civility_score": 76.3,
    "compliance_rating": "Good",
    "documents_reviewed": 3,
    "alerts_total": 5,
    "period": "2025-01-01 to 2025-06-30"
  },
  "generated_at": "2025-06-19T14:35:22Z"
}
```

---

## 🔐 Authentication (Future)

For enterprise deployments, API authentication may be required:

```http
Authorization: Bearer <jwt_token>
```

All endpoints will validate the token and return `401 Unauthorized` if invalid.

---

## 📊 Rate Limiting

| Endpoint | Rate Limit | Notes |
|----------|-----------|-------|
| `/analyze` | 60 req/min | Per client IP. |
| `/batch-analyze` | 10 req/min | Batch requests are heavier. |
| `/health` | Unlimited | No rate limiting. |
| `/export-report` | 5 req/min | Report generation is resource-intensive. |

Exceed limits → `429 Too Many Requests`.

---

## 🧪 Testing with cURL

### Basic Analysis
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "We strongly object to your position.",
    "mode": "civility",
    "include_rewrite": true
  }'
```

### Check Health
```bash
curl "http://localhost:8000/health"
```

### Batch Analysis
```bash
curl -X POST "http://localhost:8000/batch-analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      { "id": "1", "text": "Your first letter..." },
      { "id": "2", "text": "Your second letter..." }
    ]
  }'
```

---

## 🔗 Integration Examples

### JavaScript/React Frontend
```javascript
async function analyzeDraft(text, mode) {
  const response = await fetch("http://localhost:8000/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      mode,
      include_rewrite: true
    })
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  return response.json();
}

// Usage
try {
  const result = await analyzeDraft("We demand immediate compliance.", "civility");
  console.log(`Civility Score: ${result.civility_score}`);
  console.log(`Suggested Rewrite: ${result.suggested_rewrite}`);
} catch (error) {
  console.error(error);
}
```

### Python Integration
```python
import requests

def analyze_correspondence(text, mode="civility"):
    payload = {
        "text": text,
        "mode": mode,
        "include_rewrite": True
    }
    
    response = requests.post("http://localhost:8000/analyze", json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API error: {response.status_code}")

# Usage
result = analyze_correspondence("We strongly object to your position.")
print(f"Civility Score: {result['civility_score']}")
print(f"Rewrite: {result['suggested_rewrite']}")
```

---

## 🚀 Deployment Notes

### Development (Localhost)
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production (Gunicorn + HTTPS)
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

This API provides the foundation for both the Streamlit prototype and the eventual React/HTML/JS frontend.
