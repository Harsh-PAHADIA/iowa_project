# IOWA Pipeline — Intelligent Order & Workflow Automation

IOWA Pipeline is an AI-powered workflow automation system that converts manufacturing order forms into structured ERP-ready data using multimodal AI, OCR preprocessing, and automated CSV generation.

The platform streamlines manual order processing by extracting key business information from uploaded documents and transforming it into structured operational data for ERP integration.

---

## Features

### AI-Powered Data Extraction
- Utilizes Google Gemini 1.5 Flash for intelligent document understanding and structured information extraction.

### OCR & Image Enhancement
- Uses OpenCV preprocessing techniques including grayscale conversion and adaptive thresholding to improve extraction accuracy.

### ERP-Ready Automation
- Automatically converts extracted order data into clean CSV files compatible with ERP workflows.

### Workflow Optimization
- Reduces manual data entry and accelerates operational processing pipelines.

### Modern Interactive UI
- Responsive dark-themed interface with glassmorphism styling and smooth user interactions.

---

## Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- FastAPI (Python)

### AI & Processing
- Google Gemini 1.5 Flash
- OpenCV
- Pandas

---

## System Architecture

1. User uploads manufacturing order form images.
2. OpenCV preprocesses and enhances the document.
3. Gemini AI extracts structured business information.
4. Backend validates and formats extracted fields.
5. Pandas exports ERP-compatible CSV output instantly.

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- Gemini API Key

---

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
