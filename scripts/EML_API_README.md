# EML Batch Processor API

Upload `.eml` files, rename them based on sender/date/subject, and generate a combined PDF per email that includes message content plus supported attachments.

## Endpoints

- `GET /health`
- `POST /api/eml/preview`
- `POST /api/eml/process`

## Run Locally

From repo root:

```bash
python -m pip install -r requirements.api.txt
python -m uvicorn scripts.eml_batch_api:app --reload --host 0.0.0.0 --port 8000
```

Open docs at:

- `http://localhost:8000/docs`

## API Usage

### 1) Preview proposed renamed filenames

```bash
curl -X POST "http://localhost:8000/api/eml/preview" \
  -F "files=@data/emails/example.eml"
```

### 2) Process and download ZIP package

```bash
curl -X POST "http://localhost:8000/api/eml/process" \
  -F "files=@data/emails/example1.eml" \
  -F "files=@data/emails/example2.eml" \
  -o processed_emails.zip
```

Optional query param:

- `rename_only=true` to skip PDF generation.

Example:

```bash
curl -X POST "http://localhost:8000/api/eml/process?rename_only=true" \
  -F "files=@data/emails/example.eml" \
  -o renamed_only.zip
```

## ZIP Output Contents

The API returns a ZIP containing:

- Renamed `.eml` files
- Generated PDF files (unless `rename_only=true`)
- `manifest.json` summary with per-file status and attachment notes

## Limits

- Maximum files per request: `200`
- Accepted upload type: `.eml` only
