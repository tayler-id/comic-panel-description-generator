"""Complete panel analysis tool for the Comic Panel MCP Server."""

import json
import logging
from mcp.types import ErrorCode, McpError
from .detect_objects import detect_objects_tool
from .classify_scene import classify_scene_tool
from .analyze_relationships import analyze_relationships_tool
from .generate_description import generate_description_tool

logger = logging.getLogger("comic-mcp-server")

async def analyze_panel_tool(arguments, openai_key=None):
    """
    Complete analysis of a comic panel (all steps in one).
    
    Args:
        arguments (dict): Tool arguments
        openai_key (str, optional): OpenAI API key
        
    Returns:
        dict: Tool response
        
    Raises:
        McpError: If an error occurs
    """
    image_data = arguments.get("image_data")
    panel_num = arguments.get("panel_num", 1)
    is_path = arguments.get("is_path", True)
    
    if not image_data:
        raise McpError(ErrorCode.InvalidParams, "Missing image_data parameter")
    
    try:
        # Step 1: Detect objects
        objects_result = await detect_objects_tool({
            "image_data": image_data,
            "is_path": is_path
        }, openai_key)
        objects_json = json.loads(objects_result["content"][0]["text"])
        figures = objects_json.get("figures", [])
        
        # Step 2: Classify scene
        scene_result = await classify_scene_tool({
            "image_data": image_data,
            "is_path": is_path
        }, openai_key)
        scene_json = json.loads(scene_result["content"][0]["text"])
        scene_type = scene_json.get("scene_type", "unknown")
        scene_attributes = scene_json.get("attributes", [])
        
        # Step 3: Analyze relationships
        relationships_result = await analyze_relationships_tool({
            "image_data": image_data,
            "figures": figures,
            "is_path": is_path
        }, openai_key)
        relationships_json = json.loads(relationships_result["content"][0]["text"])
        relationships = relationships_json.get("relationships", [])
        
        # Step 4: Generate description
        description_result = await generate_description_tool({
            "panel_num": panel_num,
            "figures": figures,
            "scene_type": scene_type,
            "attributes": scene_attributes,
            "relationships": relationships
        }, openai_key)
        description = description_result["content"][0]["text"]
        
        # Compile complete analysis
        analysis = {
            "panel_num": panel_num,
            "figures": figures,
            "scene": {
                "type": scene_type,
                "attributes": scene_attributes
            },
            "relationships": relationships,
            "description": description
        }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(analysis, indent=2)
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error in analyze_panel_tool: {str(e)}")
        raise McpError(ErrorCode.InternalError, f"Error analyzing panel: {str(e)}")
