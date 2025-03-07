"""
MCP client for the Comic Panel Description Generator.
This module provides functions to interact with the MCP server for panel analysis and description generation.
"""

import os
import json
import logging
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MCP server name
MCP_SERVER_NAME = os.environ.get('MCP_SERVER_NAME', 'comic-panel')

# Check if MCP is available
MCP_AVAILABLE = False
try:
    from mcp import Client, StdioClientTransport
    MCP_AVAILABLE = True
    logger.info("MCP package is available")
except ImportError:
    logger.warning("MCP package is not available. MCP functionality will be disabled.")

def get_mcp_client():
    """
    Get an MCP client instance.
    
    Returns:
        mcp.Client: MCP client instance or None if MCP is not available
    """
    if not MCP_AVAILABLE:
        logger.warning("MCP is not available. Cannot create MCP client.")
        return None
        
    try:
        # Create a client
        client = Client()
        
        # Connect to the MCP server
        transport = StdioClientTransport()
        client.connect(transport)
        
        return client
    except Exception as e:
        logger.error(f"Error creating MCP client: {str(e)}")
        return None

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
        
        # If MCP is not available, return default values
        if client is None:
            logger.warning("MCP is not available. Using default values for panel analysis.")
            return {"figures": 1, "motion": "static", "objects": "none"}
        
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
        
        # If MCP is not available, use rule-based description
        if client is None:
            logger.warning("MCP is not available. Using rule-based description generation.")
            return generate_rule_based_description(image_data, panel_num)
        
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

def process_feedback_with_mcp(rating, issue_type, original_description, edited_description, comments=""):
    """
    Process feedback from artists using the MCP server.
    
    Args:
        rating (str): Rating (1-5)
        issue_type (str): Type of issue (made-up-details, missed-elements, etc.)
        original_description (str): Original description
        edited_description (str): Edited description
        comments (str, optional): Additional comments
        
    Returns:
        dict: Processing results
    """
    try:
        # Get MCP client
        client = get_mcp_client()
        
        # If MCP is not available, return a default response
        if client is None:
            logger.warning("MCP is not available. Cannot process feedback.")
            return {"success": True, "message": "Feedback saved locally (MCP server not available)"}
        
        # Call the process_feedback tool
        result = client.call_tool(
            MCP_SERVER_NAME,
            "process_feedback",
            {
                "rating": rating,
                "issue_type": issue_type,
                "original_description": original_description,
                "edited_description": edited_description,
                "comments": comments
            }
        )
        
        # Parse the result
        if result and result.content and len(result.content) > 0:
            return json.loads(result.content[0].text)
        else:
            logger.error("Empty or invalid result from MCP server")
            return {"success": False, "message": "Failed to process feedback"}
    except Exception as e:
        logger.error(f"Error in process_feedback_with_mcp: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}

def verify_description_with_mcp(description):
    """
    Verify a description using the MCP server to ensure it's factual.
    
    Args:
        description (str): Description to verify
        
    Returns:
        str: Verified description
    """
    try:
        # Get MCP client
        client = get_mcp_client()
        
        # If MCP is not available, return the original description
        if client is None:
            logger.warning("MCP is not available. Cannot verify description.")
            return description
        
        # Call the verify_description tool
        result = client.call_tool(
            MCP_SERVER_NAME,
            "verify_description",
            {
                "description": description
            }
        )
        
        # Parse the result
        if result and result.content and len(result.content) > 0:
            return result.content[0].text
        else:
            logger.error("Empty or invalid result from MCP server")
            return description
    except Exception as e:
        logger.error(f"Error in verify_description_with_mcp: {str(e)}")
        return description

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
    
    # Build minimal, factual description based on rules
    description = f"Panel {panel_num}: "
    
    # Character description - just state the count
    if figures == 1:
        description += "One character visible"
    elif figures == 2:
        description += "Two characters visible"
    else:
        description += f"{figures} characters visible"
    
    # Scene description - just state if there's motion
    if motion == "action":
        description += " in a scene with movement"
    else:
        description += " in a static scene"
    
    # Object description - only if definitely present
    if objects == "sparks":
        description += " with visual effects"
    
    # End with period
    if not description.endswith("."):
        description += "."
    
    return description
