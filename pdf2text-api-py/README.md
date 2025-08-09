# PDF2Text Extractor API (Python)

FastAPI API that provides simple HTTP endpoints to extract text from remote PDF files.

## Endpoints

- `GET /api/pdf-text?pdfUrl=[URL]&min=[START_PAGE]&max=[END_PAGE]`
  - Extracts text from a page range.
  - Defaults: `min=1`, `max=150` if not provided.
  - Constraint: `(max - min) <= 200` and pages are 1-indexed.

- `GET /api/pdf-text-all?pdfUrl=[URL]`
  - Extracts text from the whole PDF, capped to the first 200 pages.

- `GET /api/health`
  - Health check: returns `{ "status": "ok" }`.

## Requirements

- Python 3.9+

## Setup

```bash
cd /Users/aminaragrag/Desktop/cursorprojects/scrap-BO
python3 -m venv pdf2text-api-py/.venv
source pdf2text-api-py/.venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
cd pdf2text-api-py
uvicorn app.main:app --reload --port 3000
# If 3000 is in use, try: --port 3001
```

Open `http://127.0.0.1:3000/` (or the chosen port).

## Quick test

```bash
# Health
curl "http://127.0.0.1:3000/api/health"

# Extract specific pages
curl --get "http://127.0.0.1:3000/api/pdf-text" \
  --data-urlencode "pdfUrl=https://example.com/file.pdf" \
  --data-urlencode "min=1" \
  --data-urlencode "max=5"

# Extract entire PDF (first 200 pages max)
curl --get "http://127.0.0.1:3000/api/pdf-text-all" \
  --data-urlencode "pdfUrl=https://example.com/file.pdf"
```

## Response shape

```json
{
  "text": "...extracted text..."
}
```

## Notes

- CORS is enabled for all origins by default.
- For very large PDFs, only the first 200 pages are processed (to mirror the original behavior/notes).
- Output content may differ slightly from the Node.js `pdf-parse` version as this uses `pdfplumber` under the hood.

## Troubleshooting

- Address already in use: choose another port via `--port`.
- Module not found `app`: ensure you run `uvicorn` from the `pdf2text-api-py` folder where the `app/` package resides.
- SSL or download errors: the API downloads the PDF from `pdfUrl`; make sure the URL is public and reachable.

## License

MIT or your preferred license.
