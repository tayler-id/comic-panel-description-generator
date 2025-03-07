"""Relationship analysis tool for the Comic Panel MCP Server."""

import json
import numpy as np
import logging
from mcp.types import ErrorCode, McpError
from ..utils.image_utils import load_image

logger = logging.getLogger("comic-mcp-server")

async def analyze_relationships_tool(arguments, openai_key=None):
    """
    Analyze relationships between objects in a comic panel.
    
    Args:
        arguments (dict): Tool arguments
        openai_key (str, optional): OpenAI API key
        
    Returns:
        dict: Tool response
        
    Raises:
        McpError: If an error occurs
    """
    image_data = arguments.get("image_data")
    figures = arguments.get("figures", [])
    is_path = arguments.get("is_path", True)
    
    if not image_data:
        raise McpError(ErrorCode.InvalidParams, "Missing image_data parameter")
    
    try:
        # Load the image (needed for dimensions)
        img = load_image(image_data, is_path)
        height, width = img.shape[:2]
        
        # If no figures provided, return empty relationships
        if not figures:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({"relationships": []}, indent=2)
                    }
                ]
            }
        
        # Analyze spatial relationships between figures
        relationships = []
        
        # Check for figures that are close to each other
        for i, fig1 in enumerate(figures):
            for j, fig2 in enumerate(figures):
                if i >= j:  # Skip self and duplicates
                    continue
                
                # Get centers
                center1 = fig1.get("center", [0, 0])
                center2 = fig2.get("center", [0, 0])
                
                # Calculate distance between centers
                distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
                
                # Normalize distance by image diagonal
                diagonal = np.sqrt(width**2 + height**2)
                normalized_distance = distance / diagonal
                
                # Determine relationship type based on distance
                relationship_type = "near" if normalized_distance < 0.2 else "far_from"
                
                # Determine relative position
                dx = center2[0] - center1[0]
                dy = center2[1] - center1[1]
                
                position = ""
                if abs(dx) > abs(dy):
                    position = "right_of" if dx > 0 else "left_of"
                else:
                    position = "below" if dy > 0 else "above"
                
                # Add relationship
                relationships.append({
                    "figure1_id": fig1.get("id", i),
                    "figure2_id": fig2.get("id", j),
                    "type": relationship_type,
                    "position": position,
                    "distance": float(normalized_distance)
                })
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"relationships": relationships}, indent=2)
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error in analyze_relationships_tool: {str(e)}")
        raise McpError(ErrorCode.InternalError, f"Error analyzing relationships: {str(e)}")
