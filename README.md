# IOWA Pipeline - Intelligent Order & Workflow Automation

IOWA Pipeline is an AI-powered tool designed to digitize manufacturing order forms into structured ERP data. Using **Gemini 1.5 Flash**, **OpenCV**, and **FastAPI**, it extracts key information from images and exports it as an ERP-ready CSV instantly.

![IOWA Logo](https://raw.githubusercontent.com/Harsh-PAHADIA/iowa_project/main/assets/iowa_logo.png)

## Features
- **AI Extraction**: Uses Google's Gemini 1.5 Flash for high-accuracy data extraction.
- **Image Preprocessing**: OpenCV-based grayscale and adaptive thresholding for better OCR results.
- **ERP Ready**: Exports data in a clean CSV format ready for ERP import.
- **Premium UI**: Modern dark theme with glassmorphism and smooth animations.

## Tech Stack
- **Frontend**: Vanilla HTML/CSS/JS
- **Backend**: FastAPI (Python)
- **AI**: Google Gemini 1.5 Flash
- **Processing**: OpenCV, Pandas

## Getting Started

### Prerequisites
- Python 3.8+
- [Gemini API Key](https://aistudio.google.com/)

### Backend Setup
1. Navigate to the `backend` directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
4. Start the server:
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Frontend Setup
1. Navigate to the `frontend` directory.
2. Serve the static files (e.g., using Python's http.server):
   ```bash
   python -m http.server 8001
   ```
3. Open [http://localhost:8001](http://localhost:8001) in your browser.

## How it Works
1. **Upload**: Drop a manufacturing order form image.
2. **Preprocess**: OpenCV cleans and enhances the image for the AI.
3. **AI Extract**: Gemini identifies customers, dates, and order items.
4. **Export**: Pandas flattens the result into an ERP-compatible CSV.

---
Created by [Harshita Pahadia](https://github.com/Harsh-PAHADIA)
