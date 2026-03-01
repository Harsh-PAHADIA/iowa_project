# pipeline.py - IOWA Processing Pipeline  (uses new google-genai SDK)
import cv2
import json
import re
import io
import pandas as pd
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"

# ---------------------------------------------------------------------------
# Step 1 - OpenCV Image Preprocessing
# ---------------------------------------------------------------------------

def preprocess_image(input_path: str, output_path: str) -> str:
    """
    Enhances the order form image for optimal AI OCR accuracy:
      - Convert to grayscale
      - Apply adaptive Gaussian thresholding to binarise text
    """
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError(f"Could not load image at '{input_path}'. "
                         "Ensure the file is a valid image.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed = cv2.adaptiveThreshold(
        gray,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY,
        blockSize=11,
        C=2,
    )
    cv2.imwrite(output_path, processed)
    return output_path


# ---------------------------------------------------------------------------
# Step 2 - Gemini Extraction  (new google-genai SDK, v1 API)
# ---------------------------------------------------------------------------

_PROMPT = """
You are a precise data extraction assistant for manufacturing order forms.
Analyse the provided image and extract the order information.

Return ONLY a single valid JSON object - no markdown, no explanation, no code fences.

Required JSON schema:
{
  "customer_name": "<string>",
  "order_date": "<YYYY-MM-DD>",
  "items": [
    {
      "part_number": "<string>",
      "quantity": <integer>,
      "urgency": "<High | Medium | Low>"
    }
  ]
}

Rules:
- If a field is not visible, use a sensible default ("Unknown" for strings,
  0 for quantities, "Medium" for urgency).
- The items array must contain at least one entry.
- Dates must be in YYYY-MM-DD format.
""".strip()


def _clean_json(raw: str) -> str:
    """Strip any markdown code fences Gemini may wrap around its response."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    return cleaned.strip()


def extract_order_data(image_path: str) -> dict | None:
    """
    Upload the preprocessed image to Gemini and extract a strict JSON order.
    Uses the new google-genai SDK (v1 API) and inline image bytes.
    Returns the parsed dict, or None if extraction/parsing fails.
    """
    # Read image bytes and determine MIME type
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    ext = os.path.splitext(image_path)[1].lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".webp": "image/webp", ".bmp": "image/bmp"}
    mime_type = mime_map.get(ext, "image/jpeg")

    # Build the content parts
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    try:
        response = _client.models.generate_content(
            model=MODEL,
            contents=[image_part, _PROMPT],
        )
        raw_text = response.text.strip()
        cleaned = _clean_json(raw_text)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: grab the first {...} block
        try:
            start = raw_text.index("{")
            end = raw_text.rindex("}") + 1
            return json.loads(raw_text[start:end])
        except (ValueError, json.JSONDecodeError):
            return None


# ---------------------------------------------------------------------------
# Step 3 - Pandas -> ERP CSV Export
# ---------------------------------------------------------------------------

def format_for_erp(order_data: dict, output_csv: str) -> bool:
    """Flatten the nested JSON order into a tabular ERP-ready CSV."""
    if not order_data:
        return False

    rows = [
        {
            "Customer_Name": order_data.get("customer_name", "Unknown"),
            "Order_Date":    order_data.get("order_date", "Unknown"),
            "Part_Number":   item.get("part_number", "N/A"),
            "Quantity":      item.get("quantity", 0),
            "Urgency":       item.get("urgency", "Medium"),
        }
        for item in order_data.get("items", [])
    ]

    if not rows:
        return False

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    return True