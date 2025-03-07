"""Object detection tool for the Comic Panel MCP Server."""

import json
import logging
from mcp.types import ErrorCode, McpError
from ..utils.image_utils import load_image, detect_figures, detect_objects

logger = logging.getLogger("comic-mcp-server")

async def detect_objects_tool(arguments, openai_key=None):
    """
    Detect objects in a comic panel image.
    
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
        height, width = img.shape[:2]
        
        # Detect figures (characters)
        figures = detect_figures(img)
        
        # Detect special objects (like sparks)
        objects_info = detect_objects(img)
        
        # Compile results
        result = {
            "figures": figures,
            "objects": objects_info,
            "count": len(figures),
            "image_dimensions": [width, height]
        }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error in detect_objects_tool: {str(e)}")
        raise McpError(ErrorCode.InternalError, f"Error detecting objects: {str(e)}")
