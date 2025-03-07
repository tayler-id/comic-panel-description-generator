"""Scene classification tool for the Comic Panel MCP Server."""

import json
import logging
from mcp.types import ErrorCode, McpError
from ..utils.image_utils import load_image, detect_motion

logger = logging.getLogger("comic-mcp-server")

async def classify_scene_tool(arguments, openai_key=None):
    """
    Classify the scene type in a comic panel.
    
    Args:
        arguments (dict): Tool arguments
        openai_key (str, optional): OpenAI API key
        
    Returns:
        dict: Tool response
        
    Raises:
        McpError: If an error occurs
    """
    image_data = arguments.get("image_data")
    is_path = arguments.get("is_path", True)
    
    if not image_data:
        raise McpError(ErrorCode.InvalidParams, "Missing image_data parameter")
    
    try:
        # Load the image
        img = load_image(image_data, is_path)
        
        # Detect motion
        motion = detect_motion(img)
        
        # Determine scene attributes based on motion
        scene_attributes = []
        
        if motion["type"] == "action":
            scene_attributes.append("dynamic")
        else:
            scene_attributes.append("calm")
        
        # Compile scene information
        scene_info = {
            "scene_type": motion["type"],
            "attributes": scene_attributes,
            "motion": motion
        }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(scene_info, indent=2)
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error in classify_scene_tool: {str(e)}")
        raise McpError(ErrorCode.InternalError, f"Error classifying scene: {str(e)}")
