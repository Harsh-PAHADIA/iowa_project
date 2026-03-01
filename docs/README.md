# IOWA Pipeline - Intelligent Order & Workflow Automation

AI-powered full-stack PoC that digitises manufacturing order forms into structured ERP-ready CSV data.

## Architecture

```
Upload Image -> OpenCV Preprocess -> Gemini 2.5 Flash Extract -> Pandas CSV Export
```

| Layer    | Technology                        |
|----------|-----------------------------------|
| Frontend | Vanilla HTML | CSS | JavaScript   |
| Backend  | FastAPI (Python)                  |
| Vision   | OpenCV (grayscale + thresholding) |
| AI       | Google Gemini 2.5 Flash           |
| Export   | Pandas -> CSV                      |

## Project Structure

```
iowa_project/
├── backend/
│   ├── main.py          # FastAPI app & endpoints
│   ├── pipeline.py      # OpenCV + Gemini + Pandas logic
│   ├── requirements.txt # Python dependencies
│   └── .env             # GEMINI_API_KEY (not committed)
├── frontend/
│   ├── index.html       # Single-page UI
│   ├── style.css        # Premium dark theme
│   └── script.js        # Drag-drop, fetch, render logic
├── data/
│   ├── uploads/         # Raw uploaded images
│   ├── processed/       # OpenCV-cleaned images
│   └── exports/         # Generated ERP CSV files
└── docs/
    └── README.md
```

## Setup

### 1. Configure API key

```bash
echo "GEMINI_API_KEY=your_key_here" > backend/.env
```

### 2. Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start the backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Verify: `curl http://localhost:8000/api/health` -> `{"status":"ok"}`

### 4. Open the frontend

```bash
cd frontend
python3 -m http.server 5500
# → http://localhost:5500
```

Or open `frontend/index.html` directly in your browser.

## API Endpoints

| Method | Path                      | Description                  |
|--------|---------------------------|------------------------------|
| GET    | `/api/health`             | Liveness check               |
| POST   | `/api/upload`             | Process order form image     |
| GET    | `/api/download/{filename}`| Download generated ERP CSV   |

### POST `/api/upload` — Response

```json
{
  "message": "Processing complete",
  "data": {
    "customer_name": "Acme Corp",
    "order_date": "2026-02-28",
    "items": [
      { "part_number": "PN-4821", "quantity": 50, "urgency": "High" }
    ]
  },
  "download_url": "/api/download/erp_import_abc12345_form.csv"
}
```

## JSON Schema (Gemini output)

```json
{
  "customer_name": "string",
  "order_date": "YYYY-MM-DD",
  "items": [
    {
      "part_number": "string",
      "quantity": 0,
      "urgency": "High | Medium | Low"
    }
  ]
}
```