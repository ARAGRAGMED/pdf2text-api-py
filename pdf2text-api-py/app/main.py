from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import httpx
import io
import pdfplumber

app = FastAPI(title="PDF2Text Extractor API (Python)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def fetch_pdf_bytes(url: str) -> bytes:
    async with httpx.AsyncClient(headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }, timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.content


def extract_text_from_pdf(pdf_bytes: bytes, min_page: Optional[int] = None, max_page: Optional[int] = None) -> str:
    buffer = io.BytesIO(pdf_bytes)
    text_parts: List[str] = []

    with pdfplumber.open(buffer) as pdf:
        total_pages = len(pdf.pages)

        start = 1 if min_page is None else min_page
        end = total_pages if max_page is None else max_page

        if start < 1:
            raise ValueError("Invalid min page value")
        if end < 1:
            raise ValueError("Invalid max page value")
        if start > end:
            raise ValueError("Invalid page range: min > max")
        if (end - start) > 200:
            raise ValueError("The range of files is too large (it surpass 200 page)")

        # pdfplumber is 1-index vs list 0-index
        for page_index in range(start - 1, min(end, total_pages)):
            page = pdf.pages[page_index]
            page_text = page.extract_text(x_tolerance=1.5, y_tolerance=1.5) or ""
            text_parts.append(page_text)

    return "\n".join(part.strip() for part in text_parts if part is not None).strip()


@app.get("/api/pdf-text")
async def get_pdf_text(pdfUrl: Optional[str] = None, min: Optional[int] = None, max: Optional[int] = None):
    if not pdfUrl:
        raise HTTPException(status_code=400, detail={"error": "Missing pdfUrl parameter"})

    try:
        pdf_bytes = await fetch_pdf_bytes(pdfUrl)

        # Defaults to 1..150 if not provided, mirroring Node behavior
        min_page = 1 if min is None else int(min)
        max_page = 150 if max is None else int(max)

        text = extract_text_from_pdf(pdf_bytes, min_page=min_page, max_page=max_page)
        return {"text": text}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail={"error": "Failed to download PDF", "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "Invalid parameters", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Failed to process PDF", "message": str(e)})


@app.get("/api/pdf-text-all")
async def get_pdf_text_all(pdfUrl: Optional[str] = None):
    if not pdfUrl:
        raise HTTPException(status_code=400, detail={"error": "Missing pdfUrl parameter"})

    try:
        pdf_bytes = await fetch_pdf_bytes(pdfUrl)
        # Cap to first 200 pages to mirror Node's note
        text = extract_text_from_pdf(pdf_bytes, min_page=1, max_page=200)
        return {"text": text}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail={"error": "Failed to download PDF", "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "Invalid parameters", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Failed to process PDF", "message": str(e)})


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return HTMLResponse(
        content=(
            """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>PDF2Text Extractor API (Python)</title>
                    <style>
                        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }
                        code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
                        .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                    </style>
                </head>
                <body>
                    <h1>PDF2Text Extractor API (Python)</h1>
                    <p>Extract text content from PDF files using the following endpoints:</p>
                    <div class="endpoint">
                        <h3>Extract text from specific pages:</h3>
                        <code>GET /api/pdf-text?pdfUrl=[URL]&min=[START_PAGE]&max=[END_PAGE]</code>
                        <p><b>Note 1 :</b> If min equals max, the API will extract text from that specific page.</p>
                        <p><b>Note 2 :</b> The number of requested pages should not surpass 150~200 pages! (max - min <= 200).</p>
                    </div>
                    <div class="endpoint">
                        <h3>Extract text from entire PDF:</h3>
                        <code>GET /api/pdf-text-all?pdfUrl=[URL]</code>
                        <p><b>Note 1 :</b> The PDF file should not surpass 150~200 pages! (it will only extract the content of the first 200 pages).</p>
                    </div>
                    <p>Python PDF2Text Extractor API</p>
                </body>
            </html>
            """
        )
    )
