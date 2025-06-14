from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import os
from io import BytesIO
import pytesseract
from PIL import Image
import cv2
import numpy as np

app = Flask(__name__)
# Configure CORS to explicitly allow requests from your React app
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000", "supports_credentials": True}})

# Constants for SHC parsing
FIELD_PATTERNS = {
    "farmer_name": r"Farmer's Name\s*:\s*(.*)",
    "sample_no": r"Sample No\s*:\s*(.*)",
    "survey_no": r"Survey No/Khasra No\s*:\s*(.*)",
    "village": r"Village\s*:\s*(.*)",
    "gram_panchayat": r"Gram Panchayat\s*:\s*(.*)",
    "block": r"Block/Taluk/Mandal\s*:\s*(.*)",
    "district": r"District\s*:\s*(.*)",
    "state": r"State\s*:\s*(.*)",
}

NUTRIENT_PATTERNS = {
    "pH": r"pH\s*[\d.]+ to [\d.]+\s*([\d.]+)",
    "EC": r"EC \(dS/m\)\s*[\d.]+ to [\d.]+\s*([\d.]+)",
    "OC": r"OC \(%\)\s*[\d.]+ to [\d.]+\s*([\d.]+)",
    "N": r"N \(kg/ha\)\s*[\d.]+ to [\d.]+\s*([\d.]+)",
    "P": r"P \(kg/ha\)\s*[\d.]+ to [\d.]+\s*([\d.]+)",
    "K": r"K \(kg/ha\)\s*[\d.]+ to [\d.]+\s*([\d.]+)",
    "S": r"S \(ppm\)\s*[\d.]+ to [\d.]+\s*([\d.]+)",
    "Zn": r"Zn \(ppm\)\s*[\d.]+ to [\d.]+\s*([\d.]+)",
    "Fe": r"Fe \(ppm\)\s*[\d.]+ to [\d.]+\s*([\d.]+)",
    "Cu": r"Cu \(ppm\)\s*[\d.]+ to [\d.]+\s*([\d.]+)",
    "Mn": r"Mn \(ppm\)\s*[\d.]+ to [\d.]+\s*([\d.]+)",
    "B": r"B \(ppm\)\s*[\d.]+ to [\d.]+\s*([\d.]+)",
}

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Uncomment and modify the line below if you're on Windows
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route('/api/parse-shc', methods=['POST', 'OPTIONS'])
def parse_shc():
    # Handle preflight CORS requests
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file:
            # Process the uploaded image
            img_bytes = file.read()
            try:
                img = Image.open(BytesIO(img_bytes))
            except Exception as e:
                return jsonify({"error": f"Invalid image file: {str(e)}"}), 400
            
            # Convert PIL Image to OpenCV format
            img_cv = np.array(img)
            # Handle different image formats (RGB vs RGBA)
            if len(img_cv.shape) == 3 and img_cv.shape[2] == 4:  # RGBA
                img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGBA2BGR)
            elif len(img_cv.shape) == 3 and img_cv.shape[2] == 3:  # RGB
                img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
            
            # Preprocessing for better OCR
            img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            img_thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # OCR processing
            text = pytesseract.image_to_string(img_thresh)
            
            # Parse the OCR text
            data = {}
            
            # Extract farmer and location info
            for field, pattern in FIELD_PATTERNS.items():
                match = re.search(pattern, text)
                if match:
                    data[field] = match.group(1).strip()
                else:
                    data[field] = "Not found"
                    
            # Extract nutrient values
            nutrients = {}
            for nutrient, pattern in NUTRIENT_PATTERNS.items():
                match = re.search(pattern, text)
                if match:
                    try:
                        nutrients[nutrient] = float(match.group(1))
                    except ValueError:
                        nutrients[nutrient] = None
                else:
                    nutrients[nutrient] = None
            
            data["nutrients"] = nutrients
            
            return jsonify(data)
        
        return jsonify({"error": "Failed to process file"}), 500
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)