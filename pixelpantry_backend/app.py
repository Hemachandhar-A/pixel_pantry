from flask import Flask, request, jsonify, send_from_directory
import subprocess
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS
import re
import requests
import base64
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Create Flask app once
app = Flask(__name__, static_folder='static')

CORS(app, supports_credentials=True, origins="*", resources={r"/*": {"supports_credentials": True}})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/run-model', methods=['POST'])
def run_model():
    try:
        print("⚙️ Running model.py...")
        result = subprocess.run(["python", "model.py"], capture_output=True, text=True)

        print(f"✅ subprocess finished with return code: {result.returncode}")
        print(f"📝 STDOUT:\n{result.stdout}")
        print(f"❌ STDERR:\n{result.stderr}")

        if result.returncode != 0:
            return jsonify({'error': 'Failed to run model', 'details': result.stderr}), 500
            
        # Read the JSON output from the file
        try:
            with open('model_output.json', 'r') as f:
                model_result = json.load(f)
                
            # Process recommended crops
            recommended_crops = []
            for prediction in model_result.get('predictions', []):
                if 'recommended_crop' in prediction and prediction['recommended_crop'] not in recommended_crops:
                    recommended_crops.append(prediction['recommended_crop'])
            
            model_result['recommended_crops'] = recommended_crops
            
            if not recommended_crops:
                model_result['recommended_crops'] = ["No crops recommended"]
            
            return jsonify(model_result)
            
        except Exception as e:
            return jsonify({
                'error': f'Failed to read or parse JSON output file: {str(e)}',
                'stdout': result.stdout,
                'stderr': result.stderr
            }), 500

    except Exception as e:
        print(f"💥 Exception in /api/run-model: {str(e)}")
        return jsonify({'error': str(e)}), 500
@app.route('/api/explain-recommendation', methods=['POST'])
def explain_recommendation():
    try:
        data = request.json
        crop = data.get('crop')
        
        if not crop:
            return jsonify({'error': 'No crop specified'}), 400
            
        # Get general context from the data
        location = data.get('location', 'Unknown')
        n_value = data.get('N', 'Unknown')
        p_value = data.get('P', 'Unknown')
        k_value = data.get('K', 'Unknown')
        temp = data.get('predicted_avg_temp', 'Unknown')
        rainfall = data.get('predicted_total_rainfall', 'Unknown')
        ph = data.get('ph', 'Unknown')
        humidity = data.get('humidity', 'Unknown')

        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        As an agricultural AI assistant, explain why {crop} is recommended as one of the best crops for cultivation based on the following conditions:

        Location: {location}
        Soil Nutrients:
        - Nitrogen (N): {n_value}
        - Phosphorus (P): {p_value}
        - Potassium (K): {k_value}
        
        Climate and Soil Conditions:
        - Average Temperature: {temp}°C
        - Total Rainfall: {rainfall} mm
        - pH Level: {ph}
        - Humidity: {humidity}%

        Provide a concise explanation (about 150-200 words) focusing on how these specific conditions are ideal for growing {crop}. Include details about why this crop thrives in these specific soil and climate conditions.
        """

        response = model.generate_content(prompt)
        
        return jsonify({'explanation': response.text})

    except Exception as e:
        print(f"Exception in explanation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        context = data.get('context', {})
        
        # Format the context information
        recommended_crops = ", ".join(context.get('recommended_crops', ['Unknown']))
        location = context.get('location', 'Unknown')
        latitude = context.get('latitude', 'Unknown')
        longitude = context.get('longitude', 'Unknown')
        n_value = context.get('N', 'Unknown')
        p_value = context.get('P', 'Unknown')
        k_value = context.get('K', 'Unknown')
        temp = context.get('predicted_avg_temp', 'Unknown')
        rainfall = context.get('predicted_total_rainfall', 'Unknown')
        
        context_str = f"""
        Context:
        - Recommended Crops: {recommended_crops}
        - Location: {location} (Coordinates: {latitude}, {longitude})
        - Soil Nutrients: N: {n_value}, P: {p_value}, K: {k_value}
        - Climate: Average Temperature: {temp}°C, Total Rainfall: {rainfall} mm
        
        You are an agricultural expert assistant. Only answer questions related to the crop recommendations, farming practices, or agricultural topics. Keep responses concise and focused on helping the farmer understand the recommendations. If asked about topics unrelated to agriculture, politely redirect the conversation back to the crop recommendations.
        """

        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Combine context and user message
        prompt = f"{context_str}\n\nUser question: {user_message}"
        response = model.generate_content(prompt)
        
        return jsonify({'response': response.text})

    except Exception as e:
        print(f"Exception in chat: {str(e)}")
        return jsonify({'error': str(e)}), 500
        




UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Vision API configuration
API_KEY=os.getenv("API_KEY")
VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate'

def clean_text(text):
    """Clean up OCR text by removing extra spaces and normalizing line breaks"""
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Normalize newlines
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def extract_table_data(text):
    """Extract data from the soil test results table with improved row matching"""
    # Looking at the sample data, we need a more precise pattern that matches each row completely
    # This pattern matches: Sr.No, Parameter, Test Value, Unit, Rating, Normal Level
    
    # First, let's try to extract the table section
    table_section = re.search(r'Soil Test Results.*?(?=Option|Please use|Excess use)', text, re.DOTALL)
    table_text = table_section.group(0) if table_section else text
    
    # Now let's extract each row more precisely
    rows = re.findall(r'(\d+)\s+([A-Za-z\s()]+)\s+([\d.]+)\s*([a-zA-Z/%]+)?\s+([A-Za-z\s]+)\s+([\d.>-]+\s*[a-zA-Z/%\s]+)', table_text)
    
    nutrients = {}
    
    # Map for standardizing rating values
    ratings_map = {
        'low': 'Low',
        'medium': 'Medium', 
        'high': 'High',
        'sufficient': 'Sufficient',
        'moderately alkaline': 'Moderately alkaline',
        'neutral': 'Neutral'
    }
    
    for row in rows:
        try:
            sr_no, parameter, value, unit, rating, normal_level = row
            
            # Clean up parameter name and determine the nutrient key
            parameter = parameter.strip()
            
            # Determine the nutrient key based on parameter name
            if 'pH' in parameter:
                key = 'pH'
                unit = unit or ''
            elif 'EC' in parameter:
                key = 'EC'
                unit = unit or 'dS/m'
            elif 'Organic Carbon' in parameter or 'OC' in parameter:
                key = 'OC'
                unit = unit or '%'
            elif 'Nitrogen' in parameter or '(N)' in parameter:
                key = 'N'
                unit = unit or 'kg/ha'
            elif 'Phosphorus' in parameter or '(P)' in parameter:
                key = 'P'
                unit = unit or 'kg/ha'
            elif 'Potassium' in parameter or '(K)' in parameter:
                key = 'K'
                unit = unit or 'kg/ha'
            elif 'Sulphur' in parameter or '(S)' in parameter:
                key = 'S'
                unit = unit or 'ppm'
            elif 'Zinc' in parameter or '(Zn)' in parameter:
                key = 'Zn'
                unit = unit or 'ppm'
            elif 'Boron' in parameter or '(B)' in parameter:
                key = 'B'
                unit = unit or 'ppm'
            elif 'Iron' in parameter or '(Fe)' in parameter:
                key = 'Fe'
                unit = unit or 'ppm'
            elif 'Manganese' in parameter or '(Mn)' in parameter:
                key = 'Mn'
                unit = unit or 'ppm'
            elif 'Copper' in parameter or '(Cu)' in parameter:
                key = 'Cu'
                unit = unit or 'ppm'
            else:
                key = parameter
                unit = unit or ''
                
            # Clean up rating - normalize to known values
            rating = rating.strip().lower()
            for k, v in ratings_map.items():
                if k in rating:
                    rating = v
                    break
                    
            # Clean up normal level
            normal_level = normal_level.strip()
            
            # Create the nutrient entry
            nutrients[key] = {
                'value': float(value),
                'unit': unit,
                'rating': rating,
                'normal_level': normal_level
            }
        except Exception as e:
            logger.warning(f"Error extracting nutrient data from row {row}: {str(e)}")
            continue
    
    # If the standard pattern fails, try an alternative approach
    if not nutrients:
        # Alternative pattern targeting specific nutrients
        ph_match = re.search(r'pH\s+([\d.]+)\s+([A-Za-z\s]+)', table_text)
        if ph_match:
            nutrients['pH'] = {
                'value': float(ph_match.group(1)),
                'unit': '',
                'rating': ph_match.group(2).strip(),
                'normal_level': '6.5-7.5'  # Default value
            }
            
        # Similar patterns for other key nutrients
        ec_match = re.search(r'EC\s+([\d.]+)\s*dS/m\s+([A-Za-z\s]+)', table_text)
        if ec_match:
            nutrients['EC'] = {
                'value': float(ec_match.group(1)),
                'unit': 'dS/m',
                'rating': ec_match.group(2).strip(),
                'normal_level': '0-1 dS/m'  # Default value
            }
            
        # Add more specific patterns for other nutrients
    
    return nutrients

def extract_fertilizer_recommendations(text):
    """Extract fertilizer recommendations from the SHC with improved pattern matching"""
    fertilizer_recs = []
    
    # Try to find Option sections with more precise patterns
    option_pattern = r'Option\s+(\d+).*?Fertilizer Combination-(\d+).*?(?:Variet[y|ies]|Crop)'
    option_sections = re.findall(option_pattern, text, re.DOTALL)
    
    if option_sections:
        for option_num, combo_num in option_sections:
            # Find fertilizer details for this option
            # Pattern to capture the entire fertilizer table for this option
            fert_pattern = rf'Option\s+{option_num}.*?Fertilizer Combination-{combo_num}.*?(?:Option\s+\d+|If you have|Use the quantity|$)'
            fert_section = re.search(fert_pattern, text, re.DOTALL)
            
            if fert_section:
                # Extract fertilizer details from this section
                fertilizer_text = fert_section.group(0)
                
                # Try to extract crop varieties
                crops = re.findall(r'Crop Variet(?:y|ies).*?([^\n\r]+)', fertilizer_text)
                
                # Try to extract fertilizers
                fertilizers = re.findall(r'([^\n\r•,]+)(?:\s+|\n)([\d.]+\s*kg/ha)(?:\s+|\n)([^\n\r•,]+)?(?:\s+|\n)([\d.]+\s*[^\n\r•,]+)?', fertilizer_text)
                
                # Build fertilizer recommendation object
                fertilizer_object = {
                    "option": option_num,
                    "combination": combo_num,
                    "crops": crops if crops else [],
                    "fertilizers": []
                }
                
                for fert in fertilizers:
                    if len(fert) >= 2:
                        fert_obj = {
                            "name": fert[0].strip(),
                            "quantity": fert[1].strip()
                        }
                        if len(fert) >= 4 and fert[2] and fert[3]:
                            fert_obj["organic_type"] = fert[2].strip()
                            fert_obj["organic_quantity"] = fert[3].strip()
                        
                        fertilizer_object["fertilizers"].append(fert_obj)
                
                fertilizer_recs.append(fertilizer_object)
    
    # If the structured approach fails, fall back to a simpler approach
    if not fertilizer_recs:
        # Identify option sections more broadly
        option_sections = re.split(r'Option\s+\d+', text)
        if len(option_sections) > 1:
            for i, section in enumerate(option_sections[1:], 1):
                # Just capture the raw text for each option
                fertilizer_recs.append({
                    "option": str(i),
                    "text": clean_text(section)
                })
    
    return fertilizer_recs

def extract_recommendations(text):
    """Extract recommendations from the SHC with improved pattern matching"""
    recommendations = []
    
    # Match the recommendations section more precisely
    rec_section = re.search(r'(Excess use of Fertilizer is injurious to soil health and plant growth.*?)(?:Please use option|$)', text, re.DOTALL)
    
    if rec_section:
        rec_text = rec_section.group(1)
        # Split the text into lines and process each line
        lines = [line.strip() for line in rec_text.split('\n') if line.strip()]
        
        for line in lines:
            # Skip the header line
            if 'injurious to soil health' in line:
                continue
                
            # Check if this is a recommendation
            if re.match(r'^(Reclaim|Treat|Use|Adopt|Apply)', line):
                recommendations.append({"type": "Action", "text": line})
            elif ":" in line:
                parts = line.split(":", 1)
                recommendations.append({"type": parts[0].strip(), "text": parts[1].strip()})
            else:
                recommendations.append({"type": "General", "text": line})
    
    # If structured approach fails, try simple pattern matching
    if not recommendations:
        recommendation_patterns = [
            r'Reclaim[^\n]+',
            r'Treat[^\n]+',
            r'Use[^\n]+',
            r'Adopt[^\n]+'
        ]
        
        for pattern in recommendation_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                recommendations.append({"type": "Action", "text": match.strip()})
    
    return recommendations

def extract_fertilizer_recommendations(text):
    """Extract fertilizer recommendations from the SHC"""
    fertilizer_recs = []
    
    # Look for Option 1 and Option 2 sections
    options_match = re.findall(r'Option (\d)[\s\S]*?Fertilizer Combination-(\d+)[\s\S]*?(?:Option|If you have|Use the quantity|$)', text)
    
    if not options_match:
        # Try a more relaxed pattern
        option_sections = re.split(r'Option \d', text)
        if len(option_sections) > 1:
            for i, section in enumerate(option_sections[1:], 1):
                fertilizer_recs.append({
                    "option": str(i),
                    "text": clean_text(section)
                })
    else:
        for option_num, combo_num in options_match:
            # Find the content of this option
            option_pattern = rf'Option {option_num}[\s\S]*?Fertilizer Combination-{combo_num}([\s\S]*?)(?:Option|If you have|Use the quantity|$)'
            option_match = re.search(option_pattern, text)
            
            if option_match:
                fertilizer_recs.append({
                    "option": option_num,
                    "combination": combo_num,
                    "text": clean_text(option_match.group(1))
                })
    
    return fertilizer_recs

@app.route('/api/parse-shc', methods=['POST', 'OPTIONS'])
def parse_shc():
    # Handle preflight CORS requests
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        if not API_KEY:
            return jsonify({"error": "Google Cloud API Key not configured"}), 500
            
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file:
            # Read the file content
            content = file.read()
            
            # Save original image for debugging (optional)
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Convert to base64
            encoded_content = base64.b64encode(content).decode('utf-8')
            
            # Prepare request to Vision API
            request_data = {
                'requests': [
                    {
                        'image': {
                            'content': encoded_content
                        },
                        'features': [
                            {
                                'type': 'TEXT_DETECTION'
                            }
                        ]
                    }
                ]
            }
            
            # Make request to Vision API
            response = requests.post(
                f'{VISION_API_URL}?key={API_KEY}',
                data=json.dumps(request_data),
                headers={'Content-Type': 'application/json'}
            )
            
            # Check for successful response
            if response.status_code != 200:
                return jsonify({
                    "error": f"Google Vision API Error: {response.status_code}",
                    "details": response.text
                }), 500
                
            # Parse response
            result = response.json()
            
            # Check if text was detected
            if not result.get('responses') or not result['responses'][0].get('textAnnotations'):
                return jsonify({"error": "No text detected in the image"}), 400
                
            # Get full text from the first annotation
            text = result['responses'][0]['textAnnotations'][0]['description']
            
            # Save OCR text for debugging - with UTF-8 encoding
            try:
                ocr_file_path = os.path.join(UPLOAD_FOLDER, f"{file.filename.split('.')[0]}_ocr.txt")
                with open(ocr_file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                logger.info(f"OCR text saved to {ocr_file_path}")
            except Exception as e:
                logger.warning(f"Could not save OCR text to file: {str(e)}")
            
            # Create data dictionary to store the parsed information
            data = {
                "card_metadata": {},
                "farmer_details": {},
                "sample_details": {},
                "soil_info": {},
                "nutrients": {},
                "recommendations": [],
                "fertilizer_recommendations": []
            }
            
            # Extract SHC Number
            shc_number_match = re.search(r'(?:Soil Health Card Number|HP)[\s\-:/]*([A-Za-z0-9/-]+)', text)
            if shc_number_match:
                data["card_metadata"]["shc_number"] = shc_number_match.group(1).strip()
            
            # Extract validity period
            validity_match = re.search(r'Validity\s*[:-]\s*From:\s*([^\n]+)\s*To:\s*([^\n]+)', text)
            if validity_match:
                data["card_metadata"]["validity_from"] = validity_match.group(1).strip()
                data["card_metadata"]["validity_to"] = validity_match.group(2).strip()
            
            # Extract Farmer's details
            farmer_name_match = re.search(r'Farmer(?:\'s)? Name\s*:?\s*([^\n]+)', text)
            if farmer_name_match:
                data["farmer_details"]["name"] = farmer_name_match.group(1).strip()
            
            # Extract other farmer details
            father_match = re.search(r'Father(?:\'s)?/Husband Name\s*:?\s*([^\n]+)', text)
            if father_match:
                data["farmer_details"]["father_husband_name"] = father_match.group(1).strip()
            
            # Address details
            address_match = re.search(r'Address\s*:?\s*([^\n]+)', text)
            if address_match:
                data["farmer_details"]["address"] = address_match.group(1).strip()
            
            # Mobile number
            mobile_match = re.search(r'Mobile No\.\s*:?\s*([^\n]+)', text)
            if mobile_match:
                data["farmer_details"]["mobile"] = mobile_match.group(1).strip()
            
            # Gender
            gender_match = re.search(r'Gender\s*:?\s*([^\n]+)', text)
            if gender_match:
                data["farmer_details"]["gender"] = gender_match.group(1).strip()
            
            # Category
            category_match = re.search(r'Category\s*:?\s*([^\n]+)', text)
            if category_match:
                data["farmer_details"]["category"] = category_match.group(1).strip()
            
            # Sample details
            sample_date_match = re.search(r'Date of Sample Collection\s*:?\s*([^\n]+)', text)
            if sample_date_match:
                data["sample_details"]["collection_date"] = sample_date_match.group(1).strip()
            
            # Survey/Khasra/Dag number
            survey_match = re.search(r'Survey No(?:.|,|/)?\s*Khasra No(?:.|,)?/?\s*Dag No\.?\s*:?\s*([^\n]+)', text)
            if survey_match:
                data["sample_details"]["survey_number"] = survey_match.group(1).strip()
            
            # Farm Size
            farm_size_match = re.search(r'Farm Size\s*:?\s*([^\n]+)', text)
            if farm_size_match:
                data["sample_details"]["farm_size"] = farm_size_match.group(1).strip()
            
            # Geo Position
            geo_match = re.search(r'Geo Position\s*\(?GPS\)?\s*:?\s*([^\n]+)', text)
            if geo_match:
                data["sample_details"]["geo_position"] = geo_match.group(1).strip()
            
            # Soil Type
            soil_type_match = re.search(r'Soil Type\s*:?\s*([^\n]+)', text)
            if soil_type_match:
                data["soil_info"]["soil_type"] = soil_type_match.group(1).strip()
            
            # Soil Condition (specific to this card)
            soil_condition_match = re.search(r'Soil Type: Acidic hill soil', text)
            if soil_condition_match:
                data["soil_info"]["soil_condition"] = "Acidic hill soil"
            
            # District and state extraction
            district_match = re.search(r'District\s*:?\s*([^\n,]+)', text)
            if district_match:
                data["sample_details"]["district"] = district_match.group(1).strip()
            
            state_match = re.search(r'(?:State|Department of Agriculture,)\s*([^\n,]+)', text)
            if state_match:
                data["sample_details"]["state"] = state_match.group(1).strip()
            
            # Extract nutrients table data
            data["nutrients"] = extract_table_data(text)
            
            # Extract recommendations
            data["recommendations"] = extract_recommendations(text)
            
            # Extract fertilizer recommendations
            data["fertilizer_recommendations"] = extract_fertilizer_recommendations(text)
            
            # Return the parsed data
            return jsonify(data)
        
        return jsonify({"error": "Failed to process file"}), 500
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500
@app.route('/api/model/health', methods=['GET'])
def health_check1():
    return jsonify({"status": "healthy"})






from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import feedparser
import requests
import google.generativeai as genai
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



import os
import json
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from flask_cors import CORS
from werkzeug.utils import secure_filename
import zipfile
import tempfile
import shutil







from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import feedparser
import requests
import google.generativeai as genai
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



import os
import json
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from flask_cors import CORS
from werkzeug.utils import secure_filename
import zipfile
import tempfile
import shutil


# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import feedparser
import google.generativeai as genai
import logging
from werkzeug.utils import secure_filename
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import zipfile
import tempfile
import shutil
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration for Rice Disease Model
UPLOAD_FOLDER_DISEASE = 'uploads_disease'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MODEL_PATH_DISEASE = 'rice_disease_final_model.h5'

# Configuration for Rice Pest Model
UPLOAD_FOLDER_PEST = 'uploads_pest'
MODEL_PATH_PEST = 'rice_pest_final_model.h5'
DATASET_PATH_PEST = 'dataset'  # Path to your dataset with class folders for pests


app.config['UPLOAD_FOLDER_DISEASE'] = UPLOAD_FOLDER_DISEASE
app.config['UPLOAD_FOLDER_PEST'] = UPLOAD_FOLDER_PEST
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create required folders
os.makedirs(UPLOAD_FOLDER_DISEASE, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_PEST, exist_ok=True)
os.makedirs('static', exist_ok=True)

# Create the RiceDiseasePredictor class
class RiceDiseasePredictor:
    """Class for making predictions with a trained rice disease detection model."""

    def __init__(self, model_path='rice_disease_final_model.h5', class_names=None):
        """
        Initialize the predictor with a trained model.

        Args:
            model_path (str): Path to the saved model file
            class_names (list): List of class names in the same order as model output
        """
        self.model = load_model(model_path)
        self.input_shape = self.model.input_shape[1:3]  # Get expected input dimensions

        # Get the number of output classes from the model
        self.num_classes = self.model.output_shape[1]

        # If class names aren't provided, use the correct 6 rice disease classes
        if class_names is None:
            self.class_names = [
                'Bacterial Leaf Blight',
                'Brown Spot',
                'Healthy Rice Leaf',
                'Leaf Blast',
                'Leaf Scald',
                'Sheath Blight'
            ]

            # Verify that the number of classes matches the model output
            if len(self.class_names) != self.num_classes:
                print(f"⚠️ Warning (Disease): Default class names ({len(self.class_names)}) don't match model output ({self.num_classes})")
                print(f"Disease Model expects {self.num_classes} classes but we provided {len(self.class_names)} class names")
                # Fall back to generic class names if there's a mismatch
                self.class_names = [f'Disease Class {i}' for i in range(self.num_classes)]
        else:
            self.class_names = class_names
            # Verify that the number of classes matches the model output
            if len(self.class_names) != self.num_classes:
                print(f"⚠️ Warning (Disease): Provided class names ({len(self.class_names)}) don't match model output ({self.num_classes})")
                # Fall back to generic class names if there's a mismatch
                self.class_names = [f'Disease Class {i}' for i in range(self.num_classes)]

        print(f"✅ Disease Model loaded successfully. Input shape: {self.input_shape}")
        print(f"ℹ️ Disease Model predicts {self.num_classes} classes: {self.class_names}")

    def preprocess_image(self, image_path):
        img = load_img(image_path, target_size=self.input_shape)
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        preprocessed_img = preprocess_input(img_array)
        return preprocessed_img, img

    def predict(self, image_path, show_result=True, confidence_threshold=0.60):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        preprocessed_img, original_img = self.preprocess_image(image_path)
        predictions = self.model.predict(preprocessed_img, verbose=0)[0]
        if len(predictions) != len(self.class_names):
            print(f"⚠️ Warning (Disease): Model output size ({len(predictions)}) doesn't match class names ({len(self.class_names)})")
            print(f"Raw prediction (Disease): {predictions}")
            raise ValueError(f"Disease Model output size ({len(predictions)}) doesn't match class names ({len(self.class_names)})")
        predicted_idx = np.argmax(predictions)
        confidence = predictions[predicted_idx]
        if confidence < confidence_threshold:
            predicted_class = "Uncertain"
        else:
            predicted_class = self.class_names[predicted_idx]
        if show_result:
            self._display_prediction(original_img, predicted_class, confidence, predictions)
        return predicted_class, confidence, predictions

    def _display_prediction(self, img, predicted_class, confidence, all_probs):
        pass

    def batch_predict(self, image_folder, output_file=None):
        results = {}
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = [f for f in os.listdir(image_folder)
                       if os.path.splitext(f.lower())[1] in image_extensions]
        if not image_files:
            print(f"No image files found in {image_folder}")
            return results
        print(f"Found {len(image_files)} images for disease prediction. Processing...")
        for img_file in image_files:
            img_path = os.path.join(image_folder, img_file)
            try:
                predicted_class, confidence, _ = self.predict(img_path, show_result=False)
                results[img_file] = {
                    'predicted_class': predicted_class,
                    'confidence': float(confidence)
                }
                print(f"- (Disease) {img_file}: {predicted_class} ({confidence:.2%})")
            except Exception as e:
                print(f"Error processing (Disease) {img_file}: {str(e)}")
                results[img_file] = {'error': str(e)}
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=4)
                print(f"Disease prediction results saved to {output_file}")
            except Exception as e:
                print(f"Error saving disease prediction results: {str(e)}")
        return results

# Create the RicePestPredictor class
class RicePestPredictor:
    """Class for making predictions with a trained rice pest detection model."""

    def __init__(self, model_path='rice_pest_final_model.h5', class_names=None, dataset_path=DATASET_PATH_PEST):
        """
        Initialize the predictor with a trained model.

        Args:
            model_path (str): Path to the saved model file
            class_names (list): List of class names in the same order as model output
            dataset_path (str): Path to dataset directory with class folders
        """
        self.model = load_model(model_path)
        self.input_shape = self.model.input_shape[1:3]  # Get expected input dimensions

        # Get the number of output classes from the model
        self.num_classes = self.model.output_shape[1]

        # If class names aren't provided, try to detect them from the dataset directory
        if class_names is None:
            if os.path.exists(dataset_path):
                potential_class_names = sorted([folder for folder in os.listdir(dataset_path)
                                                if os.path.isdir(os.path.join(dataset_path, folder))])
                if len(potential_class_names) > 0:
                    print(f"Found {len(potential_class_names)} potential pest class names from dataset: {potential_class_names}")
                    if len(potential_class_names) == self.num_classes:
                        self.class_names = potential_class_names
                        print(f"✅ Using pest class names from dataset directory: {self.class_names}")
                    else:
                        print(f"⚠️ Warning (Pest): Dataset folder has {len(potential_class_names)} classes but model expects {self.num_classes}")
                        self._set_fallback_class_names()
                else:
                    print(f"⚠️ No class subdirectories found in {dataset_path}")
                    self._set_fallback_class_names()
            else:
                print(f"⚠️ Dataset directory not found: {dataset_path}")
                self._set_fallback_class_names()
        else:
            self.class_names = class_names
            if len(self.class_names) != self.num_classes:
                print(f"⚠️ Warning (Pest): Provided class names ({len(self.class_names)}) don't match model output ({self.num_classes})")
                self.class_names = [f'Pest Class {i}' for i in range(self.num_classes)]

        print(f"✅ Pest Model loaded successfully. Input shape: {self.input_shape}")
        print(f"ℹ️ Pest Model predicts {self.num_classes} classes: {self.class_names}")

    def _set_fallback_class_names(self):
        default_classes = [
            'Asiatic Rice Borer',
            'Brown Plant Hopper',
            'Paddy Stem Maggot',
            'Rice Gall Midge',
            'Rice Leaf Caterpillar',
            'Rice Leaf Hopper',
            'Rice Leaf Roller',
            'Rice Shell Pest',
            'Rice Stem Fly',
            'Rice Water Weevil',
            'Thrips',
            'Yellow Rice Borer'
        ]
        if len(default_classes) == self.num_classes:
            self.class_names = default_classes
            print(f"✅ Using default rice pest class names: {self.class_names}")
        else:
            self.class_names = [f'Pest Class {i}' for i in range(self.num_classes)]
            print(f"ℹ️ Using generic pest class names for {self.num_classes} classes")

    def preprocess_image(self, image_path):
        img = load_img(image_path, target_size=self.input_shape)
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        preprocessed_img = preprocess_input(img_array)
        return preprocessed_img, img

    def predict(self, image_path, show_result=True, confidence_threshold=0.60):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        preprocessed_img, original_img = self.preprocess_image(image_path)
        predictions = self.model.predict(preprocessed_img, verbose=0)[0]
        if len(predictions) != len(self.class_names):
            print(f"⚠️ Warning (Pest): Model output size ({len(predictions)}) doesn't match class names ({len(self.class_names)})")
            print(f"Raw prediction (Pest): {predictions}")
            raise ValueError(f"Pest Model output size ({len(predictions)}) doesn't match class names ({len(self.class_names)})")
        predicted_idx = np.argmax(predictions)
        confidence = predictions[predicted_idx]
        if confidence < confidence_threshold:
            predicted_class = "Uncertain"
        else:
            predicted_class = self.class_names[predicted_idx]
        if show_result:
            self._display_prediction(original_img, predicted_class, confidence, predictions)
        return predicted_class, confidence, predictions

    def _display_prediction(self, img, predicted_class, confidence, all_probs):
        pass

    def batch_predict(self, image_folder, output_file=None):
        results = {}
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = [f for f in os.listdir(image_folder)
                       if os.path.splitext(f.lower())[1] in image_extensions]
        if not image_files:
            print(f"No image files found in {image_folder}")
            return results
        print(f"Found {len(image_files)} images for pest prediction. Processing...")
        for img_file in image_files:
            img_path = os.path.join(image_folder, img_file)
            try:
                predicted_class, confidence, _ = self.predict(img_path, show_result=False)
                results[img_file] = {
                    'predicted_class': predicted_class,
                    'confidence': float(confidence)
                }
                print(f"- (Pest) {img_file}: {predicted_class} ({confidence:.2%})")
            except Exception as e:
                print(f"Error processing (Pest) {img_file}: {str(e)}")
                results[img_file] = {'error': str(e)}
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=4)
                print(f"Pest prediction results saved to {output_file}")
            except Exception as e:
                print(f"Error saving pest prediction results: {str(e)}")
        return results

# Initialize the predictors
disease_predictor = RiceDiseasePredictor(model_path=MODEL_PATH_DISEASE)
pest_predictor = RicePestPredictor(model_path=MODEL_PATH_PEST, dataset_path=DATASET_PATH_PEST)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Serve the main HTML page
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'disease_model': 'rice_disease_detection',
        'disease_model_classes': disease_predictor.class_names,
        'pest_model': 'rice_pest_detection',
        'pest_model_classes': pest_predictor.class_names
    })

# ---- Rice Disease Detection ----
@app.route('/rice-disease/predict', methods=['POST'])
def detect_rice_disease():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    logger.info(f"Processing disease detection for image: {image.filename}")

    try:
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER_DISEASE'], filename)
            image.save(filepath)
            try:
                predicted_class, confidence, all_probs = disease_predictor.predict(
                    filepath,
                    show_result=False,
                    confidence_threshold=float(request.form.get('confidence_threshold', 0.60))
                )
                probabilities = {
                    disease_predictor.class_names[i]: float(all_probs[i])
                    for i in range(len(disease_predictor.class_names))
                    }
                sorted_probs = sorted(
                    [{"class": k, "probability": v} for k, v in probabilities.items()],
                    key=lambda x: x["probability"],
                    reverse=True
                )
                response = {
                    'filename': filename,
                    'predicted_class': predicted_class,
                    'confidence': float(confidence),
                    'probabilities': probabilities,
                    'sorted_probabilities': sorted_probs,
                    'threshold_applied': float(request.form.get('confidence_threshold', 0.60))
                }
                return jsonify(response)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
            finally:
                os.remove(filepath)  # Clean up the saved file after prediction
        return jsonify({'error': 'Invalid file format. Allowed formats: png, jpg, jpeg'}), 400
    except Exception as e:
        logger.exception(f"Error processing disease detection: {str(e)}")
        return jsonify({'error': 'Error processing image for disease detection', 'details': str(e)}), 500

@app.route('/rice-disease/batch', methods=['POST'])
def batch_process_rice_disease():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.zip'):
        return jsonify({'error': 'No ZIP file selected'}), 400
    confidence_threshold = float(request.form.get('confidence_threshold', 0.60))
    temp_dir = tempfile.mkdtemp(prefix='disease_batch_')
    try:
        zip_path = os.path.join(temp_dir, 'upload.zip')
        file.save(zip_path)
        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        batch_results = disease_predictor.batch_predict(extract_dir)
        return jsonify({
            'results': batch_results,
            'total_images': len(batch_results),
            'threshold_applied': confidence_threshold
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# ---- Rice Pest Detection ----
@app.route('/rice-pest/predict', methods=['POST'])
def detect_rice_pest():
    if 'image' not in request.files:
        logger.error("No image file provided in the request")
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    logger.info(f"Processing pest detection for image: {image.filename}")

    try:
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER_PEST'], filename)
            image.save(filepath)
            try:
                predicted_class, confidence, all_probs = pest_predictor.predict(
                    filepath,
                    show_result=False,
                    confidence_threshold=float(request.form.get('confidence_threshold', 0.60))
                )
                probabilities = {
                    pest_predictor.class_names[i]: float(all_probs[i])
                    for i in range(len(pest_predictor.class_names))
                }
                sorted_probs = sorted(
                    [{"class": k, "probability": v} for k, v in probabilities.items()],
                    key=lambda x: x["probability"],
                    reverse=True
                )
                response = {
                    'filename': filename,
                    'predicted_class': predicted_class,
                    'confidence': float(confidence),
                    'probabilities': probabilities,
                    'sorted_probabilities': sorted_probs,
                    'threshold_applied': float(request.form.get('confidence_threshold', 0.60))
                }
                return jsonify(response)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
            finally:
                os.remove(filepath)  # Clean up the saved file after prediction
        return jsonify({'error': 'Invalid file format. Allowed formats: png, jpg, jpeg'}), 400
    except Exception as e:
        logger.exception(f"Error processing pest detection: {str(e)}")
        return jsonify({'error': 'Error processing image for pest detection', 'details': str(e)}), 500

@app.route('/rice-pest/batch', methods=['POST'])
def batch_process_rice_pest():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.zip'):
        return jsonify({'error': 'No ZIP file selected'}), 400
    confidence_threshold = float(request.form.get('confidence_threshold', 0.60))
    temp_dir = tempfile.mkdtemp(prefix='pest_batch_')
    try:
        zip_path = os.path.join(temp_dir, 'upload.zip')
        file.save(zip_path)
        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        batch_results = pest_predictor.batch_predict(extract_dir)
        return jsonify({
            'results': batch_results,
            'total_images': len(batch_results),
            'threshold_applied': confidence_threshold
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# ---- Other Routes ----
@app.route('/label/<image_id>', methods=['POST'])
def label_image(image_id):
    data = request.get_json()
    crop_type = data.get('cropType')
    disease_type = data.get('diseaseType')

    with open('labels.txt', 'a') as f:
        f.write(f"{image_id}: Crop={crop_type}, Disease={disease_type}\n")

    return jsonify({'message': 'Label saved successfully!'}), 200

@app.route('/news', methods=['GET'])
def get_news():
    rss_url = "https://news.google.com/rss/search?q=crop+disease+outbreak&sort=date"
    feed = feedparser.parse(rss_url)

    news_data = [{
        "headline": entry.title,
        "link": entry.link
    } for entry in feed.entries[:10]]

    return jsonify(news_data), 200

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({"answer": "Please ask a valid question."}), 400

    try:
        response = model.generate_content(question)
        answer = response.text if hasattr(response, 'text') else "Sorry, I couldn't process that request."
        return jsonify({"answer": answer}), 200
    except Exception as e:
        logger.exception(f"Exception in Gemini API request: {str(e)}")
        return jsonify({"answer": "Sorry, I couldn't process that request.", "error": str(e)}), 500

# Create the HTML file
def create_html_file():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rice Disease and Pest Detection</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .upload-section {
            margin: 20px 0;
            padding: 20px;
            border: 2px dashed #3498db;
            border-radius: 8px;
            text-align: center;
        }
        .upload-section:hover {
            background-color: #f8f9fa;
        }
        #preview {
            max-width: 100%;
            max-height: 300px;
            margin: 20px auto;
            display: none;
        }
        #results {
            margin-top: 20px;
            display: none;
        }
        .result-card {
            background: #f8f8f8;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        .progress-bar {
            height: 20px;
            position: relative;
            background: #e0e0e0;
            border-radius: 50px;
            margin: 5px 0;
        }
        .progress-bar-fill {
            height: 100%;
            border-radius: 50px;
            background: #3498db;
            transition: width 0.3s ease;
            text-align: right;
            line-height: 20px;
            color: white;
            padding-right: 10px;
            font-size: 12px;
        }
        .prediction {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            color: #2c3e50;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        #loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-radius: 50%;
            border-top: 4px solid #3498db;
            width: 40px;
            height: 40px;
            margin: 10px auto;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Rice Disease and Pest Detection</h1>

        <div class="upload-section" id="drop-area">
            <form id="upload-form">
                <p>Upload a rice plant image for analysis</p>
                <input type="file" id="file-input" accept="image/jpeg,image/png" style="display: none;">
                <button type="button" id="select-button">Select Image</button>
                <p>or drag and drop an image here</p>
            </form>
        </div>

        <img id="preview" alt="Image preview">

        <div id="loading">
            <div class="spinner"></div>
            <p>Analyzing image...</p>
        </div>

        <div id="results">
            <div class="prediction" id="prediction-text"></div>

            <div class="result-card">
                <h3>Probabilities</h3>
                <div id="probabilities"></div>
            </div>
        </div>
    </div>

    <script>
        // DOM elements
        const dropArea = document.getElementById('drop-area');
        const fileInput = document.getElementById('file-input');
        const selectButton = document.getElementById('select-button');
        const preview = document.getElementById('preview');
        const results = document.getElementById('results');
        const loading = document.getElementById('loading');
        const predictionText = document.getElementById('prediction-text');
        const probabilitiesDiv = document.getElementById('probabilities');

        // API endpoint - will be dynamically set
        let API_ENDPOINT = '';
        let analysisType = ''; // 'disease' or 'pest'

        // Handle file selection button
        selectButton.addEventListener('click', () => {
            fileInput.click();
        });

        // Handle file selection
        fileInput.addEventListener('change', handleFileSelect);

        // Handle drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            dropArea.style.backgroundColor = '#e3f2fd';
        }

        function unhighlight() {
            dropArea.style.backgroundColor = '';
        }

        dropArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            // For simplicity, assuming disease detection for drag and drop
            analysisType = 'disease';
            API_ENDPOINT = '/rice-disease/predict';
            handleFiles(files);
        }

        function handleFileSelect(e) {
            const files = e.target.files;
            // For simplicity, assuming disease detection for file select
            analysisType = 'disease';
            API_ENDPOINT = '/rice-disease/predict';
            handleFiles(files);
        }

        function handleFiles(files) {
            if (files.length) {
                const file = files[0];
                if (file.type.match('image.*')) {
                    displayPreview(file);
                    uploadFile(file);
                } else {
                    alert('Please select an image file (JPEG or PNG).');
                }
            }
        }

        function displayPreview(file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
                results.style.display = 'none';
            }
            reader.readAsDataURL(file);
        }

        function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);

            // Show loading indicator
            loading.style.display = 'block';

            fetch(API_ENDPOINT, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error analyzing image. Please try again.');
            })
            .finally(() => {
                loading.style.display = 'none';
            });
        }

        function displayResults(data) {
            // Display the main prediction
            predictionText.textContent = `Prediction: <span class="math-inline">\{data\.predicted\_class\} \(</span>{(data.confidence * 100).toFixed(1)}%)`;

            // Clear previous probabilities
            probabilitiesDiv.innerHTML = '';

            // Display probabilities as progress bars
            data.sorted_probabilities.forEach(item => {
                const probability = item.probability * 100;
                const barContainer = document.createElement('div');
                barContainer.innerHTML = `
                    <div style="display: flex; justify-content:space-between; margin-bottom: 5px;">
                        <span>${item.class}</span>
                        <span>${probability.toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill" style="width: ${probability}%"></div>
                    </div>
                `;
                probabilitiesDiv.appendChild(barContainer);
            });

            // Show results
            results.style.display = 'block';
        }
    </script>
</body>
</html>
"""

    os.makedirs('static', exist_ok=True)
    with open('static/index.html', 'w') as f:
        f.write(html_content)

    print("✅ HTML file created at 'static/index.html'")

# Debugging: Print a message to confirm explicit key usage
logger.info("Using explicit Gemini API key.")

# Ensure 'uploads' directory exists
os.makedirs("uploads", exist_ok=True)

# Explicitly set Gemini API Key inside configure function
genai.configure(api_key="AIzaSyAAFKI2vwESBrFJZfl5X5daXrepc72TftM")  # Replace with actual API key

# Gemini model setup
model = genai.GenerativeModel('gemini-1-5-flash')

# Home route
@app.route("/")
def home():
    return "Flask server is running!"

if __name__ == '__main__':
    create_html_file()
    app.run(debug=True, host='0.0.0.0', port=5000)