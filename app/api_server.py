"""
API server for the Comic Panel Description Generator.
This module provides a Flask API server that can be used by the main app.
"""

import os
import base64
import json
import logging
import tempfile
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check if we should use local processing or MCP
USE_MCP = os.environ.get('USE_MCP', 'false').lower() == 'true'

if USE_MCP:
    # Import MCP client
    logger.info("Using MCP for processing")
    from mcp_client import analyze_panel_with_mcp, generate_description_with_mcp
else:
    # Import local processing modules
    logger.info("Using local processing")
    from vision import analyze_panel
    from textgen import generate_description

# Create Flask app
app = Flask(__name__)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze a comic panel image.
    
    Request body:
        {
            "image_data": "base64 encoded image or path",
            "is_path": boolean,
            "panel_num": integer
        }
    
    Returns:
        {
            "figures": integer,
            "motion": "action" or "static",
            "objects": "sparks" or "none"
        }
    """
    try:
        # Get request data
        data = request.json
        if not data:
            raise BadRequest("Missing request body")
        
        image_data = data.get('image_data')
        is_path = data.get('is_path', False)
        
        if not image_data:
            raise BadRequest("Missing image_data parameter")
        
        # Process the image
        if is_path:
            # Use the path directly
            if USE_MCP:
                result = analyze_panel_with_mcp(image_data)
            else:
                result = analyze_panel(image_data)
        else:
            # Save base64 data to a temporary file
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp:
                    temp_path = temp.name
                    # Decode base64 data
                    image_bytes = base64.b64decode(image_data)
                    temp.write(image_bytes)
                
                # Process the temporary file
                if USE_MCP:
                    result = analyze_panel_with_mcp(temp_path)
                else:
                    result = analyze_panel(temp_path)
                
                # Clean up
                os.unlink(temp_path)
            except Exception as e:
                logger.error(f"Error processing base64 image: {str(e)}")
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in /api/analyze: {str(e)}")
        return jsonify({
            "error": str(e),
            "figures": 1,
            "motion": "static",
            "objects": "none"
        }), 500

@app.route('/api/describe', methods=['POST'])
def describe():
    """
    Generate a description for a comic panel.
    
    Request body:
        {
            "image_data": {
                "figures": integer,
                "motion": "action" or "static",
                "objects": "sparks" or "none"
            },
            "panel_num": integer
        }
    
    Returns:
        {
            "description": string
        }
    """
    try:
        # Get request data
        data = request.json
        if not data:
            raise BadRequest("Missing request body")
        
        image_data = data.get('image_data')
        panel_num = data.get('panel_num', 1)
        
        if not image_data:
            raise BadRequest("Missing image_data parameter")
        
        # Generate description
        if USE_MCP:
            description = generate_description_with_mcp(image_data, panel_num)
        else:
            description = generate_description(image_data, panel_num)
        
        return jsonify({"description": description})
    
    except Exception as e:
        logger.error(f"Error in /api/describe: {str(e)}")
        return jsonify({
            "error": str(e),
            "description": f"Panel {panel_num}: Error generating description."
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('API_PORT', 8001))
    app.run(host='0.0.0.0', port=port)
