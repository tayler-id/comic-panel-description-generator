"""
MCP client for the Comic Panel Description Generator.
This module provides functions to interact with the MCP server for panel analysis and description generation.
"""

import os
import json
import logging
import base64
from mcp import Client, StdioClientTransport

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MCP server name
MCP_SERVER_NAME = os.environ.get('MCP_SERVER_NAME', 'comic-panel')

def get_mcp_client():
    """
    Get an MCP client instance.
    
    Returns:
        mcp.Client: MCP client instance
    """
    try:
        # Create a client
        client = Client()
        
        # Connect to the MCP server
        transport = StdioClientTransport()
        client.connect(transport)
        
        return client
    except Exception as e:
        logger.error(f"Error creating MCP client: {str(e)}")
        raise

def analyze_panel_with_mcp(image_path):
    """
    Analyze a comic panel using the MCP server.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Analysis results
    """
    try:
        # Get MCP client
        client = get_mcp_client()
        
        # Call the analyze_panel tool
        result = client.call_tool(
            MCP_SERVER_NAME,
            "analyze_panel",
            {
                "image_data": image_path,
                "panel_num": 1,
                "is_path": True
            }
        )
        
        # Parse the result
        if result and result.content and len(result.content) > 0:
            analysis = json.loads(result.content[0].text)
            
            # Extract the relevant information
            figures_count = len(analysis.get("figures", []))
            scene_type = analysis.get("scene", {}).get("type", "static")
            
            # Check for objects like sparks
            objects_type = "none"
            for figure in analysis.get("figures", []):
                if figure.get("type") == "sparks":
                    objects_type = "sparks"
                    break
            
            # Return in the format expected by the app
            return {
                "figures": figures_count,
                "motion": scene_type,
                "objects": objects_type
            }
        else:
            logger.error("Empty or invalid result from MCP server")
            return {"figures": 1, "motion": "static", "objects": "none"}
    except Exception as e:
        logger.error(f"Error in analyze_panel_with_mcp: {str(e)}")
        return {"figures": 1, "motion": "static", "objects": "none"}

def generate_description_with_mcp(image_data, panel_num=1):
    """
    Generate a description for a comic panel using the MCP server.
    
    Args:
        image_data (dict): Analysis data
        panel_num (int): Panel number
        
    Returns:
        str: Generated description
    """
    try:
        # Get MCP client
        client = get_mcp_client()
        
        # Convert the image_data to the format expected by the MCP server
        figures = []
        for i in range(image_data.get("figures", 1)):
            figures.append({
                "id": i,
                "type": "character",
                "bbox": [0, 0, 100, 100],  # Placeholder
                "area": 10000,  # Placeholder
                "center": [50, 50]  # Placeholder
            })
        
        # Call the generate_description tool
        result = client.call_tool(
            MCP_SERVER_NAME,
            "generate_description",
            {
                "panel_num": panel_num,
                "figures": figures,
                "scene_type": image_data.get("motion", "static"),
                "attributes": ["dynamic" if image_data.get("motion") == "action" else "calm"],
                "relationships": []
            }
        )
        
        # Parse the result
        if result and result.content and len(result.content) > 0:
            return result.content[0].text
        else:
            logger.error("Empty or invalid result from MCP server")
            return generate_rule_based_description(image_data, panel_num)
    except Exception as e:
        logger.error(f"Error in generate_description_with_mcp: {str(e)}")
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
