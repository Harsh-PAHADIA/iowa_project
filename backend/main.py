# main.py — IOWA Backend (FastAPI)
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from pipeline import preprocess_image, extract_order_data, format_for_erp
import shutil
import uuid

# ---------------------------------------------------------------------------
# Absolute path setup — works regardless of CWD
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent          # iowa_project/
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR   = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORTS_DIR   = DATA_DIR / "exports"

for d in (UPLOADS_DIR, PROCESSED_DIR, EXPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(title="IOWA Pipeline API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Liveness probe."""
    return {"status": "ok", "service": "IOWA Pipeline API"}


@app.post("/api/upload")
async def upload_and_process(file: UploadFile = File(...)):
    """
    Full IOWA pipeline:
      1. Validate & save uploaded image
      2. OpenCV preprocessing (grayscale + adaptive threshold)
      3. Gemini 1.5 Flash extraction → strict JSON schema
      4. Pandas → CSV for ERP import
      5. Return JSON data + CSV download URL
    """
    # --- Validate file type ---
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. "
                   f"Please upload JPEG, PNG, WEBP, or BMP."
        )

    try:
        # 1. Save uploaded file with a unique prefix to avoid collisions
        uid = uuid.uuid4().hex[:8]
        safe_name = f"{uid}_{file.filename}"
        input_path = UPLOADS_DIR / safe_name
        with open(input_path, "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        # 2. OpenCV preprocessing
        processed_path = PROCESSED_DIR / f"clean_{safe_name}"
        preprocess_image(str(input_path), str(processed_path))

        # 3. Gemini extraction
        extracted_data = extract_order_data(str(processed_path))
        if not extracted_data:
            raise HTTPException(
                status_code=422,
                detail="AI extraction failed - could not parse a valid JSON order from the image."
            )

        # 4. Pandas → CSV
        stem = Path(file.filename).stem
        csv_filename = f"erp_import_{uid}_{stem}.csv"
        csv_path = EXPORTS_DIR / csv_filename
        format_for_erp(extracted_data, str(csv_path))

        return {
            "message": "Processing complete",
            "data": extracted_data,
            "download_url": f"/api/download/{csv_filename}",
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Serve the generated ERP CSV file."""
    # Prevent path traversal
    if "/" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    file_path = EXPORTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(path=str(file_path), filename=filename, media_type="text/csv")