import os
import uuid
import base64
import json
import requests
import logging
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

# API configuration
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000/api')
API_TIMEOUT = 30  # seconds

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_for_testing')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_panel_api(image_path):
    """
    Call the API to analyze a comic panel.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Analysis results
    """
    try:
        # Check if we should use local processing or API
        if API_BASE_URL:
            logger.info(f"Using API at {API_BASE_URL} for panel analysis")
            
            # Convert image to base64
            with open(image_path, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Call the API
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                json={"image_data": encoded_image, "is_path": False, "panel_num": 1},
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"API analysis successful: {result}")
                return result
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                # Fall back to default values
                return {"figures": 1, "motion": "static", "objects": "none"}
        else:
            # If no API URL is configured, use the MCP server directly
            logger.info("Using MCP server directly for panel analysis")
            
            # Import the MCP client only when needed
            from mcp_client import analyze_panel_with_mcp
            
            # Call the MCP client
            result = analyze_panel_with_mcp(image_path)
            logger.info(f"MCP analysis successful: {result}")
            return result
            
    except Exception as e:
        logger.error(f"Error in analyze_panel_api: {str(e)}")
        # Return default values in case of error
        return {"figures": 1, "motion": "static", "objects": "none"}

def generate_description_api(image_data, panel_num=1):
    """
    Call the API to generate a description for a comic panel.
    
    Args:
        image_data (dict): Analysis data
        panel_num (int): Panel number
        
    Returns:
        str: Generated description
    """
    try:
        # Check if we should use local processing or API
        if API_BASE_URL:
            logger.info(f"Using API at {API_BASE_URL} for description generation")
            
            # Call the API
            response = requests.post(
                f"{API_BASE_URL}/describe",
                json={"image_data": image_data, "panel_num": panel_num},
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                description = result.get("description", "")
                logger.info(f"API description generation successful: {description}")
                return description
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                # Fall back to rule-based description
                return generate_rule_based_description(image_data, panel_num)
        else:
            # If no API URL is configured, use the MCP server directly
            logger.info("Using MCP server directly for description generation")
            
            # Import the MCP client only when needed
            from mcp_client import generate_description_with_mcp
            
            # Call the MCP client
            description = generate_description_with_mcp(image_data, panel_num)
            logger.info(f"MCP description generation successful: {description}")
            return description
            
    except Exception as e:
        logger.error(f"Error in generate_description_api: {str(e)}")
        # Fall back to rule-based description
        return generate_rule_based_description(image_data, panel_num)

def generate_rule_based_description(image_data, panel_num):
    """
    Generate a rule-based description as a fallback.
    
    Args:
        image_data (dict): Analysis data
        panel_num (int): Panel number
        
    Returns:
        str: Generated description
    """
    logger.info("Generating rule-based description")
    
    # Extract data from image analysis
    figures = image_data.get("figures", 1)
    motion = image_data.get("motion", "static")
    objects = image_data.get("objects", "none")
    
    # Build description
    description = f"Panel {panel_num}: "
    
    # Character description
    if figures == 1:
        description += "A single character"
    elif figures == 2:
        description += "Two characters"
    else:
        description += f"{figures} characters"
    
    # Scene description
    if motion == "action":
        description += " in a scene with movement"
    else:
        description += " in a calm, static scene"
    
    # Object description
    if objects == "sparks":
        description += " with visual effects like sparks or impact lines"
    
    # Additional context based on figure count
    if figures == 1:
        description += ". The character appears to be the focus of this panel."
    elif figures == 2:
        description += ". The characters appear to be interacting with each other."
    else:
        description += ". The characters appear to be part of a group scene."
    
    return description

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Generate a unique filename to prevent collisions
            filename = str(uuid.uuid4()) + secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Process the image using the API
                image_data = analyze_panel_api(filepath)
                
                # Generate description using the API
                panel_num = 1  # For MVP, we assume a single panel
                description = generate_description_api(image_data, panel_num)
                
                # Clean up the file after processing
                os.remove(filepath)
                
                return render_template('result.html', description=description, image_data=image_data)
            
            except Exception as e:
                # Clean up the file in case of error
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash(f'Error processing image: {str(e)}')
                return redirect(request.url)
    
    return render_template('index.html')

@app.errorhandler(413)
def too_large(e):
    return render_template('index.html', error="File too large! Maximum size is 16MB."), 413

@app.errorhandler(500)
def server_error(e):
    return render_template('index.html', error="Server error! Please try again later."), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
